import time
import os
import shutil
import pandas as pd
import requests
from playwright.async_api import Page
from src.scripts.base import BaseScraper, ScraperResult
from src.logger import logger
from src.config import settings

class RelatorioConclusos(BaseScraper):
    def __init__(self):
        super().__init__()
        # Caminho final do CSV (Google Drive)
        self.output_csv_path = r"G:\Meu Drive\Processos_Conclusos.csv"
        # Webhook URL
        self.webhook_url = "https://n8n.maicondener.dev.br/webhook/planilha-processos-gabinete"

    async def run(self, page: Page) -> ScraperResult:
        start_time = time.time()
        self.logger.info("Iniciando automação: Relatório de Processos Conclusos")

        try:
            # 1. Navegar e Logar (Login é tratado na base se não estiver logado)
            await self.navigate_to_home(page)
            await self.login(page)

            # 2. Pesquisar no menu e acessar "Relatórios Estatísticos"
            self.logger.info("Buscando 'Relatórios Estatísticos'...")
            
            # 1. Expandir menu "Relatórios"
            self.logger.info("Expandindo menu 'Relatórios'...")
            await page.get_by_role("link", name="Relatórios", exact=True).click()
            
            # 2. Clicar no link "Relatórios Estatísticos"
            self.logger.info("Clicando em 'Relatórios Estatísticos'...")
            
            # Se o link estiver visível, clica. Se estiver em um menu colapsado, talvez precise expandir.
            # O usuário forneceu o seletor exato.
            await page.get_by_role("link", name="Relatórios Estatísticos", exact=True).click()
            
            # Aguarda carregamento da página de relatórios (iframe ou nova página)
            await page.wait_for_load_state("domcontentloaded")
            
            # 3. Selecionar "Processos Conclusos no 1º Grau - Vara"
            self.logger.info("Selecionando relatório...")
            
            # Seleciona o relatório usando o label fornecido
            await page.get_by_label("Selecione o Relatório:").select_option(label="Processos Conclusos no 1º Grau - Vara")

            # 4. Clicar em Pesquisar
            self.logger.info("Pesquisando (Aguardando até 5 min)...")
            # Aumentando timeout para 5 minutos pois relatórios podem demorar
            await page.locator("#divInfraBarraComandosSuperior").get_by_role("button", name="Pesquisar").click(timeout=300000)
            
            # Aguarda processamento
            await page.wait_for_timeout(2000)

            # 5. Gerar Excel (Download)
            self.logger.info("Iniciando processo de download do Excel (aguardando até 10 min)...")
            
            # Prepara o listener de download com timeout estendido
            async with page.expect_download(timeout=600000) as download_info:
                # Clica no botão "Gerar Excel" sem esperar por navegação,
                # pois a ação apenas dispara um download em segundo plano.
                await page.locator("#divInfraBarraComandosSuperior").get_by_role("button", name="Gerar Excel").click(no_wait_after=True)
            
            download = await download_info.value
            temp_path = os.path.join(os.getcwd(), "data", "temp_download.xlsx")
            await download.save_as(temp_path)
            self.logger.info(f"Download concluído: {temp_path}")

            # Carrega o Excel para o DataFrame
            df = pd.read_excel(temp_path)

            # 6. Integrar com LegalMind Core
            self.logger.info("Integrando dados com o LegalMind Core...")
            try:
                from src.utils.integracao_legalmind import enviar_relatorio_concluso
                
                records = []
                # Converter DataFrame para lista de dicionários para a API
                for _, row in df.iterrows():
                    # Normaliza colunas mapeando do Excel do Eproc (19 colunas)
                    records.append({
                        "localidade": str(row.get('LOCALIDADE', '')),
                        "vara": str(row.get('VARA', '')),
                        "competencia": str(row.get('COMPETENCIA', '')),
                        "numero_processo": str(row.get('PROCESSO', row.get('Nº do Processo', ''))),
                        "data_autuacao": str(row.get('DATA_AUTUACAO', '')),
                        "classe": str(row.get('CLASSE', '')),
                        "codigo_classe": str(row.get('CODIGO_CLASSE', '')),
                        "situacao_classe": str(row.get('SITUACAO_CLASSE', '')),
                        "assunto": str(row.get('ASSUNTO', '')),
                        "codigo_assunto": str(row.get('CODIGO_ASSUNTO', '')),
                        "movimento": str(row.get('MOVIMENTO', '')),
                        "codigo_movimento": str(row.get('CODIGO_MOVIMENTO', '')),
                        "data_movimento": str(row.get('DATA_MOVIMENTO', '')),
                        "dias_conclusos": int(row.get('DIAS', 0)) if pd.notnull(row.get('DIAS')) else 0,
                        "parte_autora": str(row.get('PARTE_AUTORA', '')),
                        "parte_reu": str(row.get('PARTE_REU', '')),
                        "ultimo_localizador": str(row.get('ULTIMO LOCALIZADOR', '')),
                        "pessoa_situacao_rua": str(row.get('PESSOA EM SITUACAO DE RUA', '')),
                        "magistrado": str(row.get('MAGISTRADO', '')),
                        
                        # Campos Extras/Derivados
                        "tipo_conclusao": str(row.get('TIPO', '')), # Pode não existir neste layout novo, mas mantemos
                        "data_conclusao": str(row.get('DATA DA CONCLUSÃO', '')), # Idem
                        "observacao": str(row.get('OBSERVAÇÕES', '')), # Idem
                        
                        "dados_snapshot": row.dropna().to_dict() # Remove NaNs para o JSON
                    })
                
                success = enviar_relatorio_concluso(records)
            except Exception as ie:
                self.logger.error(f"Falha na integração com LegalMind: {ie}")
                success = False

            # Limpa temporário
            if os.path.exists(temp_path):
                os.remove(temp_path)

            execution_time = time.time() - start_time
            msg_status = "Sucesso" if success else "Falha na API"
            
            return ScraperResult(
                success=success,
                data={"total_processado": len(df)},
                message=f"Fluxo finalizado: {msg_status}. {len(df)} processos processados.",
                execution_time=execution_time
            )

        except Exception as e:
            self.logger.exception(f"Erro no fluxo RelatorioConclusos: {e}")
            return ScraperResult(
                success=False,
                message=str(e),
                execution_time=time.time() - start_time
            )
