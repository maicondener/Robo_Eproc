from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel
from playwright.async_api import Page
from src.logger import logger
from src.config import settings

class ScraperResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: str
    execution_time: float = 0.0

class BaseScraper(ABC):
    def __init__(self):
        self.logger = logger

    @abstractmethod
    async def run(self, page: Page) -> ScraperResult:
        """
        Método principal que deve ser implementado por todos os scripts.
        Recebe uma página do Playwright e retorna um ScraperResult.
        """
        pass

    async def navigate_to_home(self, page: Page):
        """
        Navega para a URL base configurada no sistema.
        """
        url = settings.EPROC_URL
        self.logger.info(f"Navegando para a página inicial: {url}")
        await page.goto(url)

    async def login(self, page: Page):
        """
        Método auxiliar para realizar login no Eproc.
        Pode ser reutilizado pelos scripts que precisam de autenticação.
        """
        self.logger.info("Iniciando processo de login...")
        
        # Garante que estamos na página correta antes de logar
        if page.url == "about:blank":
             await self.navigate_to_home(page)

        # TODO: Implementar a lógica real de login do Eproc aqui
        # Por enquanto, apenas simula o uso das credenciais
        if not settings.EPROC_LOGIN or not settings.EPROC_SENHA:
            self.logger.warning("Credenciais de login não configuradas corretamente.")
            return

        # Exemplo de fluxo de login (adaptar para o Eproc real)
        # await page.fill("#txtUsuario", settings.EPROC_LOGIN)
        # await page.fill("#pwdSenha", settings.EPROC_SENHA)
        # await page.click("#sbmEntrar")
        
        self.logger.info(f"Login simulado para usuário: {settings.EPROC_LOGIN}")
