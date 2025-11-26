import time
from playwright.async_api import Page
from src.scripts.base import BaseScraper, ScraperResult

class LocPeticoes(BaseScraper):
    async def run(self, page: Page) -> ScraperResult:
        """
        Script de extração da lista de processos do localizador PETIÇÕES.
        """
        start_time = time.time()
        self.logger.info("Executando a extração dos processos do localizador PETIÇÕES.")
        
        try:
            # Navega para a URL configurada no .env (EPROC_URL)
            await self.navigate_to_home(page)
            
            # Realiza o login
            await self.login(page)

            # time.sleep(10) # Removido após testes

            execution_time = time.time() - start_time
            return ScraperResult(
                success=True,
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

