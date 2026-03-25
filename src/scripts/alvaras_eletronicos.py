import time
import os
import pandas as pd
from datetime import datetime, timedelta
from playwright.async_api import Page
from src.scripts.base import BaseScraper, ScraperResult
from src.config import settings
from src.utils.google_drive import search_file_in_drive, download_from_drive, update_file_in_drive, upload_to_drive

class AlvarasEletronicos(BaseScraper):
    def __init__(self):
        super().__init__()
        self.file_name = 'dataset_alvarás.xlsx'

    async def run(self, page: Page) -> ScraperResult:
        start_time = time.time()
        self.logger.info('Iniciando automação: Relatório de Alvarás Eletrônicos (Versão Refatorada)')

        try:
            # 1. Navegar e Logar
            await self.navigate_to_home(page)
            await self.login(page)

            # 2. Pesquisa na sidebar e navegação no menu
            self.logger.info("Pesquisando 'Relatório Alvará Eletrônico' na sidebar...")
            
            # Preencher o campo de pesquisa da sidebar
            sidebar_search = page.locator('#sidebar-searchbox')
            await sidebar_search.wait_for(state='visible')
            await sidebar_search.fill('Relatório Alvará Eletrônico')
            await sidebar_search.press('Enter')
            
            # Clicar no link que aparece como resultado
            self.logger.info("Link filtrado. Clicando em 'Relatório Alvará Eletrônico'...")
            # O seletor provido pelo usuário é exato: link com aria-label correspondente
            relatorio_link = page.locator('a[aria-label="Relatório Alvará Eletrônico"]')
            await relatorio_link.wait_for(state='visible', timeout=10000)
            await relatorio_link.click()
            
            # Aguarda carregamento do formulário
            await page.wait_for_load_state('networkidle')
            
            # 3. Preencher Filtros do Formulário
            self.logger.info('Preenchendo formulário...')
            
            # Selecionar o órgão: TODIA1ECIV (value=270000100)
            self.log_success('Selecionando Órgão: TODIA1ECIV')
            await page.locator('#selOrgao').select_option(value='270000100')
            
            # Calcular a data de ontem (ontem é feriado ou final de semana, o eproc aceita qualquer data válida)
            # O input type="date" espera o formato yyyy-mm-dd
            ontem_dt = datetime.now() - timedelta(days=1)
            data_str = ontem_dt.strftime('%Y-%m-%d')
            self.logger.info(f'Preenchendo datas com: {data_str}')
            
            # Preencher datas de início e fim
            await page.locator('#txtDataInicio').fill(data_str)
            await page.locator('#txtDataFim').fill(data_str)
            
            # 4. Clicar no botão 'Buscar Alvarás'
            self.logger.info('Buscando Alvarás...')
            await page.locator('#sbmBuscar').click()
            
            # Aguarda a tela de resultados
            await page.wait_for_load_state('networkidle')
            
            # 5. Gerar Excel Analítico (Download)
            # A página possui 2 botões com id="btnexcel" (Sintético e Analítico),
            # por isso usamos get_by_role com o texto exato para evitar ambiguidade
            self.logger.info('Iniciando download do Excel Analítico...')
            
            btn_excel = page.get_by_role('button', name='Gerar Excel Analítico')
            await btn_excel.wait_for(state='visible', timeout=30000)
            
            async with page.expect_download(timeout=120000) as download_info:
                await btn_excel.click(no_wait_after=True)
            
            download = await download_info.value
            temp_dir = os.path.join(os.getcwd(), settings.TEMP_DOWNLOAD_DIR)
            os.makedirs(temp_dir, exist_ok=True)
            novo_arquivo_path = os.path.join(temp_dir, 'novo_alvara.xlsx')
            await download.save_as(novo_arquivo_path)
            self.log_success(f'Relatório baixado em: {novo_arquivo_path}')

            # 6. Processar Dados e Sincronizar com Google Drive
            self.logger.info('Processando arquivo Excel...')
            # O eproc costuma gerar arquivos com título na primeira linha.
            # Segundo o usuário, as linhas 1 e 2 são o cabeçalho, então usamos header=1
            # para que a segunda linha seja considerada o nome das colunas.
            df_novo = pd.read_excel(novo_arquivo_path, header=1)
            
            if df_novo.empty:
                self.logger.warning('O relatório baixado está vazio.')
            
            self.logger.info(f"Verificando existência de '{self.file_name}' no Drive...")
            file_id = search_file_in_drive(self.file_name)
            
            temp_final_path = os.path.join(temp_dir, self.file_name)
            
            if file_id:
                self.logger.info(f'Arquivo existente encontrado (ID: {file_id}). Baixando para mesclar...')
                arquivo_antigo_path = os.path.join(temp_dir, 'old_alvara.xlsx')
                
                if download_from_drive(file_id, arquivo_antigo_path):
                    df_antigo = pd.read_excel(arquivo_antigo_path)
                    
                    # Alinhar colunas do novo ao antigo para evitar duplicação de cabeçalho
                    # Usa as colunas do arquivo existente como referência
                    df_novo_alinhado = pd.DataFrame(df_novo.values, columns=df_antigo.columns[:len(df_novo.columns)])
                    
                    # Adicionar dados novos ao final dos dados antigos
                    df_final = pd.concat([df_antigo, df_novo_alinhado], ignore_index=True)
                    df_final.to_excel(temp_final_path, index=False)
                    self.logger.info(f'Dados mesclados. Total de linhas: {len(df_final)}')
                    
                    self.logger.info('Atualizando arquivo no Google Drive...')
                    update_file_in_drive(file_id, temp_final_path)
                    self.log_success('Planilha atualizada no Google Drive com sucesso!')
                else:
                    self.logger.error('Falha ao baixar arquivo antigo do Drive.')
                    # Tenta apenas salvar o novo se falhar download mas já existir no Drive? 
                    # Melhor não sobrescrever um arquivo grande se a conexão falhou.
                    raise Exception('Não foi possível baixar o arquivo base para atualização.')
            else:
                self.logger.info('Criando novo arquivo no Drive...')
                df_novo.to_excel(temp_final_path, index=False)
                upload_to_drive(temp_final_path, self.file_name)
                self.log_success('Novo dataset criado no Google Drive!')

            # 7. Limpeza e Finalização
            for p in [novo_arquivo_path, temp_final_path, os.path.join(temp_dir, 'old_alvara.xlsx')]:
                if os.path.exists(p):
                    os.remove(p)

            execution_time = time.time() - start_time
            return ScraperResult(
                success=True,
                data={'rows_added': len(df_novo)},
                message=f'Alvarás processados: {len(df_novo)} registros adicionados em {self.file_name}.',
                execution_time=execution_time
            )

        except Exception as e:
            self.logger.exception(f'Erro durante a execução do script: {str(e)}')
            return ScraperResult(
                success=False,
                message=f'Falha na execução: {str(e)}',
                execution_time=time.time() - start_time
            )
