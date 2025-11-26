import time
from playwright.async_api import Page
from src.scripts.base import BaseScraper, ScraperResult

class ExemploScraper(BaseScraper):
    async def run(self, page: Page) -> ScraperResult:
        """
        Script de exemplo: navega até example.com, espera 2 segundos e retorna o título da página.
        """
        start_time = time.time()
        self.logger.info("Executando script de exemplo...")
        
        try:
            await page.goto("http://example.com")
            
            self.logger.info("Aguardando 2 segundos...")
            time.sleep(2) # Usando sleep síncrono para simples demonstração
            
            title = await page.title()
            self.logger.info(f"Título da página: {title}")
            
            execution_time = time.time() - start_time
            return ScraperResult(
                success=True,
                data={"title": title},
                message="Extração concluída com sucesso",
                execution_time=execution_time
            )
        except Exception as e:
            self.logger.error(f"Erro durante a execução: {e}")
            return ScraperResult(
                success=False,
                message=f"Erro: {str(e)}",
                execution_time=time.time() - start_time
            )

# Função auxiliar para manter compatibilidade ou facilitar instanciacao se necessario
# Mas a ideia é que o main.py instancie a classe.

