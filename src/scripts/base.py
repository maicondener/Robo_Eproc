from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel
from playwright.async_api import Page
from src.logger import logger
from src.config import settings
import pyotp

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

        # Aguarda o carregamento da página
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

        # Verifica se já estamos logados
        try:
            if "eprocV2_prod_1grau" in page.url and "txtUsuario" not in await page.content():
                 self.logger.info("Sessão válida detectada. Pulando login.")
                 return
        except Exception:
            pass

        try:
            self.logger.info("Tentando realizar login...")
            # Preenche usuário e senha usando seletores por ID (mais robustos)
            # Fallback para get_by_role se ID falhar
            try:
                await page.locator("#txtUsuario").fill(settings.EPROC_LOGIN)
            except Exception:
                self.logger.warning("ID #txtUsuario não encontrado, tentando get_by_role...")
                await page.get_by_role("textbox", name="Usuário").fill(settings.EPROC_LOGIN)

            try:
                pwd_field = page.locator("#pwdSenha")
                await pwd_field.fill(settings.EPROC_SENHA)
            except Exception:
                pwd_field = page.get_by_role("textbox", name="Senha")
                await pwd_field.fill(settings.EPROC_SENHA)
            
            # Tenta submeter o formulário pressionando Enter no campo de senha
            self.logger.info("Submetendo formulário via Enter...")
            await pwd_field.press("Enter")
            
            # --- TRATAMENTO DE 2FA (TOTP) ---
            # Verifica se apareceu o campo de 2FA
            try:
                if settings.EPROC_2FA_SECRET:
                    self.logger.info("Verificando a necessidade de autenticação de dois fatores (2FA)...")

                    # Seletor combinado que tenta encontrar o campo 2FA de várias maneiras
                    combined_selector = (
                        "#txtAcessoCodigo, "
                        "input[placeholder*='Código' i], "
                        "input[name*='token' i]"
                    )
                    
                    two_fa_field = page.locator(combined_selector)
                    
                    try:
                        # Espera pelo campo aparecer com um timeout razoável
                        self.logger.info("Aguardando campo de 2FA...")
                        await two_fa_field.wait_for(state="visible", timeout=7000)
                    except Exception:
                        # Se o campo não aparecer, provavelmente o login ocorreu sem 2FA ou falhou antes
                        self.logger.debug("Campo de 2FA não foi exibido em 7s. Prosseguindo...")
                        # A verificação de login ocorrerá naturalmente depois

                    if await two_fa_field.is_visible():
                        self.logger.info("Campo de 2FA encontrado. Preenchendo código...")
                        totp = pyotp.TOTP(settings.EPROC_2FA_SECRET)
                        code = totp.now()
                        self.logger.info(f"Gerando código 2FA: {code}")
                        
                        await two_fa_field.fill(code)
                        await two_fa_field.press("Enter")
                    else:
                        self.logger.warning("Campo de 2FA não foi encontrado. O login pode ter falhado ou não foi necessário 2FA.")

            except Exception as e:
                self.logger.debug(f"Nenhum desafio 2FA detectado ou erro ao processar: {e}")

            # --- SELEÇÃO DE PERFIL (Opcional) ---
            if settings.EPROC_PERFIL:
                self.logger.info(f"Verificando seleção de perfil: '{settings.EPROC_PERFIL}'...")
                try:
                    # Tenta encontrar o perfil em um botão ou link (conforme relato do usuário)
                    # Usa um seletor combinado para achar qualquer um dos dois
                    perfil_selector = f"button:has-text('{settings.EPROC_PERFIL}'), a:has-text('{settings.EPROC_PERFIL}')"
                    
                    # Aguarda um pouco para ver se a tela de perfil aparece
                    try:
                        # Timeout curto para detecção
                        await page.wait_for_selector(perfil_selector, timeout=1000)
                        self.logger.info(f"Perfil '{settings.EPROC_PERFIL}' encontrado. Clicando...")
                        
                        # Clica e aguarda a navegação acontecer
                        await page.click(perfil_selector)
                        await page.wait_for_load_state("networkidle")
                        
                    except Exception:
                        self.logger.debug(f"Perfil '{settings.EPROC_PERFIL}' não encontrado como botão/link ou não foi necessário selecionar.")
                        # Tenta fallback genérico se não achou
                        try:
                             await page.click(f"text={settings.EPROC_PERFIL}", timeout=1000)
                             await page.wait_for_load_state("networkidle")
                        except:
                             pass
                        
                except Exception as e:
                    self.logger.warning(f"Erro ao tentar selecionar perfil: {e}")

            self.logger.info(f"Login realizado para usuário: {settings.EPROC_LOGIN}")
            
            # Salva o estado da sessão (cookies, storage) para próximas execuções
            await page.context.storage_state(path="state.json")
            self.logger.info("Sessão salva em 'state.json'")
            
        except Exception as e:
            self.logger.error(f"Erro ao realizar login: {e}")
            raise e
