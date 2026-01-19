import time
import re
from playwright.async_api import Page
from src.scripts.base import BaseScraper, ScraperResult
from src.utils.csv_handler import save_to_csv

class LocBaseScraper(BaseScraper):
    """
    Classe base para scripts que extraem processos de um localizador específico.
    As subclasses devem definir LOCATOR_NAME e OUTPUT_FILENAME.
    """
    LOCATOR_NAME: str = ""       # Ex: "PETIÇÃO"

    async def run(self, page: Page) -> ScraperResult:
        if not self.LOCATOR_NAME:
            raise ValueError("As subclasses de LocBaseScraper devem definir LOCATOR_NAME.")

        start_time = time.time()
        self.logger.info(f"Executando a extração dos processos do localizador '{self.LOCATOR_NAME}'.")

        try:
            # Navega para a home
            await self.navigate_to_home(page)

            # Realiza o login
            await self.login(page)

            # --- NAVEGAÇÃO ESPECÍFICA ---
            self.logger.info(f"Navegando para 'Processos com Localizador {self.LOCATOR_NAME}'...")
            
            # Constrói o regex dinamicamente com base no nome do localizador
            # Escapa o nome para evitar problemas com caracteres especiais no regex
            escaped_name = re.escape(self.LOCATOR_NAME)
            regex_pattern = re.compile(rf"^Processos\s+com\s+Localizador\s+[\"']?{escaped_name}[\"']?$", re.IGNORECASE)

            try:
                await page.get_by_role("cell", name=regex_pattern).click()
            except Exception as e:
                self.logger.warning(f"Clique por role falhou ({e}), tentando por texto genérico...")
                # Fallback: clica em qualquer elemento que tenha o texto chave
                await page.locator(f"text=Processos com Localizador {self.LOCATOR_NAME}").first.click()
            
            # Aguarda a tabela carregar
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
                await page.wait_for_timeout(2000) 
            except Exception:
                self.logger.warning("Timeout esperando load state, prosseguindo...")
            
            processos_encontrados = []
            pagina_atual = 1
            
            while True:
                self.logger.info(f"Processando página {pagina_atual}...")
                
                texto_pagina = ""
                tabelas = await page.locator("table").all()
                for tabela in tabelas:
                    if await tabela.is_visible():
                        texto_pagina += await tabela.inner_text() + "\n"
                
                if not texto_pagina.strip():
                    texto_pagina = await page.content()

                matches = re.findall(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", texto_pagina)
                
                novos_processos = list(set(matches))
                self.logger.info(f"Encontrados {len(novos_processos)} processos nesta página.")
                processos_encontrados.extend(novos_processos)
                
                # --- PAGINAÇÃO ---
                next_page_li = page.locator("#lnkInfraProximaPaginaSuperior")
                
                if await next_page_li.is_visible():
                    class_attr = await next_page_li.get_attribute("class")
                    if class_attr and "disabled" in class_attr:
                        self.logger.info("Fim da paginação (botão desabilitado).")
                        break
                    
                    self.logger.info("Indo para a próxima página...")
                    await next_page_li.locator("a").click()
                    
                    try:
                        await page.wait_for_load_state("domcontentloaded", timeout=10000)
                        await page.wait_for_timeout(1000) 
                    except Exception:
                        self.logger.warning("Timeout na paginação, tentando seguir...")
                    
                    pagina_atual += 1
                else:
                    proxima_pagina_btn = page.locator("a[title='Próxima Página'], a:has-text('Próxima >')").first
                    if await proxima_pagina_btn.is_visible():
                         await proxima_pagina_btn.click()
                         pagina_atual += 1
                    else:
                        self.logger.info("Fim da paginação (botão não encontrado).")
                        break

            processos_unicos = list(set(processos_encontrados))
            self.logger.info(f"Total de processos únicos extraídos: {len(processos_unicos)}")

            # --- INTEGRAÇÃO LEGALMIND (Fluxo Primário) ---
            integrado = False
            msg_integracao = "Integração não realizada."
            try:
                from src.utils.integracao_legalmind import enviar_para_legalmind
                integrado = enviar_para_legalmind(processos_unicos, localizador=self.LOCATOR_NAME)
                msg_integracao = "Processos enviados com sucesso para o LegalMind Core." if integrado else "Falha ao enviar processos para a API."
            except Exception as ie:
                self.logger.error(f"Erro na integração direta: {ie}")
                msg_integracao = f"Erro técnico na integração: {ie}"

            execution_time = time.time() - start_time
            return ScraperResult(
                success=integrado, # Agora o sucesso do scraper depende da integração
                data={
                    "processos": processos_unicos, 
                    "total": len(processos_unicos),
                    "integrado": integrado
                },
                message=f"Extração concluída. {msg_integracao}",
                execution_time=execution_time
            )

        except Exception as e:
            self.logger.error(f"Erro durante a execução: {e}")
            return ScraperResult(
                success=False,
                data=None,
                message=str(e),
                execution_time=time.time() - start_time
            )
