from playwright.async_api import Page
import time

async def run(page: Page) -> dict:
    """
    Script de exemplo: navega até example.com, espera 2 segundos e retorna o título da página.
    """
    print("Executando script de exemplo...")
    await page.goto("http://example.com")
    
    print("Aguardando 2 segundos...")
    time.sleep(2) # Usando sleep síncrono para simples demonstração
    
    title = await page.title()
    print(f"Título da página: {title}")
    
    return {"title": title}

