import time
from playwright.async_api import Page, expect
from src.scripts.base import BaseScraper, ScraperResult

class ExemploScraper(BaseScraper):
    async def run(self, page: Page) -> ScraperResult:
        """
        Script de exemplo didático demonstrando as principais funcionalidades do Playwright.
        
        Este script não realiza uma extração real do Eproc, mas serve como guia
        de como interagir com elementos web (clicar, preencher, ler texto, etc).
        """
        start_time = time.time()
        self.logger.info("Iniciando script de demonstração do Playwright...")
        
        try:
            # 1. NAVEGAÇÃO
            # ==================================================================
            # O método self.navigate_to_home(page) usa a URL definida no .env
            # Mas você pode navegar para qualquer URL com page.goto()
            self.logger.info("1. Navegação")
            await page.goto("https://demo.playwright.dev/todomvc/") 
            # Usamos um site de demo público para este exemplo funcionar de verdade
            
            # 2. SELETORES E INTERAÇÃO (Locators)
            # ==================================================================
            # O Playwright recomenda usar "Locators" que são resilientes a mudanças.
            # Documentação: https://playwright.dev/python/docs/locators
            
            self.logger.info("2. Interagindo com elementos")
            
            # Exemplo: Encontrar um campo de entrada pelo placeholder e preencher
            input_tarefa = page.get_by_placeholder("What needs to be done?")
            await input_tarefa.fill("Aprender Playwright no Robô Eproc")
            await input_tarefa.press("Enter") # Pressionar tecla
            
            await input_tarefa.fill("Revisar a documentação")
            await input_tarefa.press("Enter")

            # 3. CLIQUES E AÇÕES
            # ==================================================================
            # Exemplo: Clicar em um checkbox. 
            # Aqui usamos um seletor CSS simples para variar, mas prefira get_by_role se possível.
            # .toggle é a classe do checkbox no site de demo
            checkbox = page.locator(".toggle").first 
            await checkbox.click()
            
            # 4. EXTRAÇÃO DE DADOS (Scraping)
            # ==================================================================
            self.logger.info("3. Extraindo dados")
            
            # Pegar o texto de um elemento
            # Vamos pegar a contagem de itens restantes
            contador = page.locator(".todo-count")
            texto_contador = await contador.inner_text()
            self.logger.info(f"Texto extraído: {texto_contador}")
            
            # Pegar um atributo (ex: href de um link, value de um input)
            valor_input = await input_tarefa.get_attribute("placeholder")
            self.logger.info(f"Placeholder do input: {valor_input}")

            # 5. ASSERÇÕES (Validações)
            # ==================================================================
            # O Playwright tem 'expect' para garantir que a página está no estado esperado.
            # Isso é ótimo para garantir que o robô não tente agir antes da hora.
            self.logger.info("4. Realizando validações (Assertions)")
            
            # Verifica se o texto "1 item left" está visível na página
            await expect(contador).to_contain_text("1 item left")
            
            # 6. ESPERAS EXPLÍCITAS (Evite se puder, use Locators/Expects)
            # ==================================================================
            # O Playwright espera automaticamente pelos elementos, mas às vezes
            # precisamos esperar algo específico.
            # await page.wait_for_selector(".minha-classe")
            # await page.wait_for_timeout(2000) # Espera fixa (não recomendado em produção)

            # --- FIM DO EXEMPLO ---
            
            execution_time = time.time() - start_time
            return ScraperResult(
                success=True,
                data={
                    "demo_url": page.url,
                    "itens_restantes": texto_contador,
                    "exemplo_concluido": True
                },
                message="Demonstração do Playwright concluída com sucesso!",
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"Erro durante a demonstração: {e}")
            # Em caso de erro, podemos tirar um screenshot para debug
            await page.screenshot(path="logs/erro_demo.png")
            
            return ScraperResult(
                success=False,
                message=f"Erro na demonstração: {str(e)}",
                execution_time=time.time() - start_time
            )


