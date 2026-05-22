import os
import re
import time

import pandas as pd
from playwright.async_api import Page

from src.config import settings
from src.scripts.base import BaseScraper, ScraperResult
from src.utils.google_sheets import salvar_processos_no_sheets


class LocBaseScraper(BaseScraper):
    """
    Classe base para scripts que extraem processos de um localizador específico.
    As subclasses devem definir LOCATOR_NAME.
    """

    LOCATOR_NAME: str = ''  # Ex: 'MANDADOS - CITAÇÃO/INTIMAÇÃO ELETRÔNICA'
    SPREADSHEET_ID: str = '1ZoB5WItw1KwY4zIkrfLhAtWmgIDMbLNJRaCSM0Il6po'

    async def run(self, page: Page) -> ScraperResult:
        if not self.LOCATOR_NAME:
            raise ValueError('As subclasses de LocBaseScraper devem definir LOCATOR_NAME.')

        start_time = time.time()
        self.logger.info(
            f'Executando a extração dos processos do localizador "{self.LOCATOR_NAME}".'
        )

        excel_path = None
        try:
            # 1. Navega para a home e realiza o login
            await self.navigate_to_home(page)
            await self.login(page)
            await page.wait_for_load_state('networkidle')

            # Verificação de Redirecionamento (Sessão Expirada)
            if 'txtUsuario' in await page.content():
                self.logger.warning('Sessão expirada. Tentando logar novamente...')
                await self.login(page)
                await page.wait_for_load_state('networkidle')

            # 2. Navegação via Sidebar para "Localizadores do órgão"
            self.logger.info('Pesquisando "Localizadores do órgão" na sidebar...')
            sidebar_search = page.locator('#sidebar-searchbox')
            await sidebar_search.wait_for(state='visible', timeout=30000)
            await sidebar_search.fill('Localizadores do órgão')
            await sidebar_search.press('Enter')

            # Clicar no link "Localizadores do Órgão" resultante
            self.logger.info('Clicando no link "Localizadores do Órgão"...')
            # Busca especificamente o link com aria-label exato ou link que contenha a ação de listagem correspondente
            relatorio_link = page.locator(
                'a[aria-label="Localizadores do Órgão"], a[href*="acao=localizador_orgao_listar"]'
            ).first
            await relatorio_link.wait_for(state='visible', timeout=20000)
            await relatorio_link.click()

            # 3. Filtrar pelo nome do localizador específico
            self.logger.info(f'Filtrando pelo localizador: "{self.LOCATOR_NAME}"...')
            input_locator = page.locator('#txtSiglaDescricaoLocalizador')
            await input_locator.wait_for(state='visible', timeout=20000)
            await input_locator.fill(self.LOCATOR_NAME)
            await page.locator('#btnFiltro').click()
            await page.wait_for_load_state('networkidle')

            # 4. Clicar no link de "Total de processos" correspondente ao localizador de forma resiliente
            self.logger.info('Localizando o link "Total de processos" na tabela de resultados...')

            # Busca todas as linhas da tabela de resultados
            rows = await page.locator('table tr, tr').all()
            target_row = None

            for r in rows:
                if await r.is_visible():
                    row_text = await r.inner_text()
                    # Compara ignorando diferenças de caixa (case-insensitive) e espaços em branco
                    clean_row_text = ' '.join(row_text.lower().split())
                    clean_locator_name = ' '.join(self.LOCATOR_NAME.lower().split())
                    if clean_locator_name in clean_row_text:
                        target_row = r
                        break

            if target_row is None:
                raise Exception(
                    f'Linha correspondente ao localizador "{self.LOCATOR_NAME}" não foi encontrada na tabela.'
                )

            # Busca a âncora de processos de forma ultra resiliente
            # Prioridade 1: Link que aponte para a ação de listagem de processos do localizador no eproc
            total_processos_link = target_row.locator(
                'a[href*="localizador_processos_listar"]'
            ).first

            # Prioridade 2 (Fallback): Qualquer link cujo texto contenha apenas números (Total de Processos)
            if not await total_processos_link.is_visible():
                self.logger.info(
                    'Link por href de listagem não está visível, tentando fallback por conteúdo numérico...'
                )
                anchors = await target_row.locator('a').all()
                for a in anchors:
                    a_text = (await a.inner_text()).strip()
                    if a_text.isdigit() and int(a_text) >= 0:
                        total_processos_link = a
                        break

            # Verifica se o link foi finalmente encontrado e se é visível
            if not await total_processos_link.is_visible():
                raise Exception(
                    f'Link "Total de processos" não encontrado ou indisponível na linha do localizador "{self.LOCATOR_NAME}".'
                )

            total_txt = (await total_processos_link.inner_text()).strip()
            self.logger.info(
                f'Link correspondente encontrado com valor "{total_txt}". Acessando relatório de processos...'
            )
            await total_processos_link.click()
            await page.wait_for_load_state('networkidle')

            # 5. Baixar a planilha Excel clicando no botão #sbmExcel de forma resiliente
            self.logger.info(
                'Iniciando o download do arquivo Excel com o relatório de processos...'
            )
            # O eproc costuma duplicar o botão sbmExcel na barra superior e inferior da página, usamos .first para evitar strict mode
            btn_excel = page.locator('#sbmExcel').first
            await btn_excel.wait_for(state='visible', timeout=20000)

            async with page.expect_download(timeout=120000) as download_info:
                await btn_excel.click(no_wait_after=True)

            download = await download_info.value
            temp_dir = os.path.join(os.getcwd(), settings.TEMP_DOWNLOAD_DIR)
            os.makedirs(temp_dir, exist_ok=True)
            # Remove caracteres especiais inválidos para nomes de arquivos
            clean_locator_filename = re.sub(r'[\\/*?:"<>|]', '_', self.LOCATOR_NAME)
            excel_filename = f'temp_{clean_locator_filename.replace(" ", "_")}.xlsx'
            excel_path = os.path.join(temp_dir, excel_filename)
            await download.save_as(excel_path)
            self.logger.info(f'Arquivo Excel baixado com sucesso em: {excel_path}')

            # 6. Ler a planilha Excel baixada usando pandas
            self.logger.info('Lendo arquivo Excel e processando colunas...')

            # Tenta ler com header=1 primeiro, que é o padrão do eproc com linha de sumário informativa
            df = pd.read_excel(excel_path, header=1, dtype=str)

            if df.empty:
                self.logger.warning('O relatório baixado está vazio.')
                return ScraperResult(
                    success=True,
                    data={'processos_adicionados': 0, 'total_original': 0},
                    message='O relatório do localizador está vazio no eproc.',
                    execution_time=time.time() - start_time,
                )

            # Limpa espaços no nome das colunas
            df.columns = [c.strip() for c in df.columns]

            # Identifica as colunas necessárias de forma flexível e tolerante a falhas
            col_processo = None
            col_data = None

            def encontrar_colunas(columns):
                p_col = None
                d_col = None
                for c in columns:
                    c_lower = c.lower()
                    if (
                        'número processo' in c_lower
                        or 'numero processo' in c_lower
                        or 'processo' in c_lower
                        or 'pocesso' in c_lower
                    ):
                        p_col = c
                        break
                for c in columns:
                    c_lower = c.lower()
                    if (
                        'inclusão no localizador' in c_lower
                        or 'inclusao no localizador' in c_lower
                        or 'inclusão' in c_lower
                        or 'inclusao' in c_lower
                        or 'data' in c_lower
                    ):
                        d_col = c
                        break
                return p_col, d_col

            col_processo, col_data = encontrar_colunas(df.columns)

            # Fallback caso a planilha não tenha o sumário no topo (lendo com header=0)
            if not col_processo or not col_data:
                self.logger.info(
                    'Colunas esperadas não encontradas com header=1. Tentando com header=0...'
                )
                df_fallback = pd.read_excel(excel_path, header=0, dtype=str)
                df_fallback.columns = [c.strip() for c in df_fallback.columns]
                p_fallback, d_fallback = encontrar_colunas(df_fallback.columns)
                if p_fallback and d_fallback:
                    df = df_fallback
                    col_processo = p_fallback
                    col_data = d_fallback
                    self.logger.info('Colunas encontradas com header=0!')

            if not col_processo:
                raise KeyError(
                    f'Coluna de "Número Processo" não encontrada nas colunas da planilha: {df.columns.tolist()}'
                )
            if not col_data:
                raise KeyError(
                    f'Coluna de "Inclusão no localizador" não encontrada nas colunas da planilha: {df.columns.tolist()}'
                )

            self.logger.info(
                f'Mapeamento das colunas do Excel: Processo -> "{col_processo}", Data Inclusão -> "{col_data}"'
            )

            # Prepara a lista de dicionários com chaves normalizadas
            dados_brutos = []
            regex_processo = re.compile(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')

            for _, row_df in df.iterrows():
                proc_val = str(row_df[col_processo]).strip()
                data_val = str(row_df[col_data]).strip()

                # Extrai apenas o número do processo limpo por regex
                match = regex_processo.search(proc_val)
                if match:
                    dados_brutos.append({'processo': match.group(0), 'data_inclusao': data_val})

            self.logger.info(f'Total de processos capturados do Excel: {len(dados_brutos)}')

            # 7. Sincronizar com o Google Sheets aplicando a lógica de unicidade (Processo, Data)
            self.logger.info('Iniciando sincronização com a planilha do Google Sheets...')
            processos_ineditos = salvar_processos_no_sheets(
                spreadsheet_id=self.SPREADSHEET_ID, dados_processos=dados_brutos
            )

            # 8. Integração com o LegalMind Core (apenas processos inéditos)
            integrado = False
            msg_integracao = 'Nenhum processo inédito para integrar.'

            if processos_ineditos:
                self.logger.info(
                    f'Enviando {len(processos_ineditos)} processos inéditos para o LegalMind Core...'
                )
                try:
                    from src.utils.integracao_legalmind import enviar_para_legalmind

                    integrado = enviar_para_legalmind(
                        processos_ineditos, localizador=self.LOCATOR_NAME
                    )
                    msg_integracao = (
                        'Processos inéditos enviados com sucesso para o LegalMind Core.'
                        if integrado
                        else 'Falha ao enviar processos inéditos para a API.'
                    )
                except Exception as ie:
                    self.logger.error(f'Erro na integração direta com o LegalMind: {ie}')
                    msg_integracao = f'Erro técnico na integração com o LegalMind: {ie}'
            else:
                # Se não houver novos inéditos, o scraper foi um sucesso de validação/checagem
                integrado = True
                self.logger.info(
                    'Sincronização concluída. Nenhum novo processo para integrar no LegalMind.'
                )

            execution_time = time.time() - start_time
            return ScraperResult(
                success=integrado,
                data={
                    'processos_adicionados': len(processos_ineditos),
                    'total_original': len(dados_brutos),
                    'integrado': integrado,
                },
                message=f'Extração e gravação em lote finalizada. {msg_integracao}',
                execution_time=execution_time,
            )

        except Exception as e:
            self.logger.error(f'Erro crítico durante a execução do extrator de localizador: {e}')
            return ScraperResult(
                success=False, data=None, message=str(e), execution_time=time.time() - start_time
            )
        finally:
            # 9. Limpar arquivos temporários
            if excel_path and os.path.exists(excel_path):
                try:
                    os.remove(excel_path)
                    self.logger.info('Arquivo Excel temporário removido.')
                except Exception as ex_del:
                    self.logger.error(
                        f'Erro ao remover arquivo temporário no bloco finally: {ex_del}'
                    )
