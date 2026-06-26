import requests
import urllib3
from urllib.parse import urlparse

from src.logger import logger
from src.config import settings

# Desabilita avisos de segurança para requisições HTTPS sem verificação de certificado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_CONNECT_TIMEOUT = 3


def _api_base_url() -> str:
    url = settings.LEGALMIND_API_URL or 'http://localhost:8000/api/v1/'
    parsed = urlparse(url)
    return f'{parsed.scheme}://{parsed.netloc}'


def _ping_api() -> bool:
    try:
        health_url = f'{_api_base_url()}/api/v1/health/'
        resp = requests.get(health_url, timeout=_CONNECT_TIMEOUT, verify=False)
        return resp.status_code < 500
    except Exception:
        return False


def ensure_legalmind_running(verbose: bool = False) -> bool:
    """
    Verifica se a API LegalMind está acessível.
    Retorna True se estiver respondendo, ou False caso contrário.
    """
    if _ping_api():
        logger.debug('LegalMind API está ativa e respondendo.')
        return True

    if verbose:
        logger.error(
            f'LegalMind API não responde no endereço configurado: {settings.LEGALMIND_API_URL}. '
            'Certifique-se de que a API está rodando e que o endereço está correto no arquivo .env.'
        )
    return False

