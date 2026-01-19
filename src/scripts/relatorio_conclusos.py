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

            # 6. Converter para CSV e Salvar no G Drive
            self.logger.info("Convertendo para CSV...")
            
            # Ler Excel (usa openpyxl via pandas)
            df = pd.read_excel(temp_path)
            
            # Salvar CSV
            # Certifica-se que o diretório destino existe (G drive deve estar montado)
            output_dir = os.path.dirname(self.output_csv_path)
            if not os.path.exists(output_dir) and os.path.exists("G:\\"):
                # Se G existe mas a pasta não, tenta criar (embora G: geralmente seja drive virtual)
                try:
                    os.makedirs(output_dir, exist_ok=True)
                except:
                    pass

            # Salva
            df.to_csv(self.output_csv_path, index=False, encoding='utf-8')
            self.logger.info(f"Arquivo salvo em: {self.output_csv_path}")

            # Limpa temporário
            if os.path.exists(temp_path):
                os.remove(temp_path)

            # 7. Integrar com LegalMind Core (Nova Tabela)
            self.logger.info("Integrando dados com o LegalMind Core...")
            try:
                from src.utils.integracao_legalmind import enviar_relatorio_concluso
                
                records = []
                # Converter DataFrame para lista de dicionários para a API
                for _, row in df.iterrows():
                    # Normaliza colunas comuns do Eproc
                    records.append({
                        "numero_processo": str(row.get('Processo', row.get('Nº do Processo', ''))),
                        "magistrado": str(row.get('Magistrado', '')),
                        "dias_conclusos": int(row.get('Dias', row.get('Qt. Dias', 0))) if pd.notnull(row.get('Dias', row.get('Qt. Dias'))) else 0,
                        "dados_snapshot": row.dropna().to_dict() # Remove NaNs para o JSON
                    })
                
                enviar_relatorio_concluso(records)
            except Exception as ie:
                self.logger.error(f"Falha na integração com LegalMind: {ie}")

            # 8. Webhook (Opcional, mantido como redundância)
            self.logger.info("Enviando Webhook...")
            payload = [{"nome_planilha": "Processos_Conclusos.csv"}]
            response = requests.post(self.webhook_url, json=payload, headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                self.logger.info("Webhook enviado com sucesso!")
            else:
                self.logger.error(f"Erro ao enviar webhook: {response.status_code} - {response.text}")

            execution_time = time.time() - start_time
            return ScraperResult(
                success=True,
                data={"csv_path": self.output_csv_path, "total_processado": len(df)},
                message=f"Fluxo finalizado. {len(df)} processos enviados para o LegalMind Core.",
                execution_time=execution_time
            )

        except Exception as e:
            self.logger.exception(f"Erro no fluxo RelatorioConclusos: {e}")
            return ScraperResult(
                success=False,
                message=str(e),
                execution_time=time.time() - start_time
            )
