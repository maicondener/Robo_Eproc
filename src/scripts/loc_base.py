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
    OUTPUT_FILENAME: str = ""    # Ex: "processos_peticao.csv"

    async def run(self, page: Page) -> ScraperResult:
        if not self.LOCATOR_NAME or not self.OUTPUT_FILENAME:
            raise ValueError("As subclasses de LocBaseScraper devem definir LOCATOR_NAME e OUTPUT_FILENAME.")

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

            csv_path = save_to_csv(processos_unicos, filename=self.OUTPUT_FILENAME)

            execution_time = time.time() - start_time
            return ScraperResult(
                success=True,
                data={
                    "processos": processos_unicos, 
                    "total": len(processos_unicos),
                    "csv_path": csv_path
                },
                message=f"Extração concluída. CSV salvo em: {csv_path}",
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
