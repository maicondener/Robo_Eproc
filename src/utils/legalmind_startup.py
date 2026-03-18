import sys
import time
import subprocess
import platform
import requests
from urllib.parse import urlparse

from src.logger import logger
from src.config import settings

_COMPOSE_PATH_LINUX   = "/mnt/c/LegalMind"
_COMPOSE_PATH_WINDOWS = r"C:\LegalMind"
_POLL_RETRIES  = 30   # 30 × 3 s = 90 s máximo
_POLL_INTERVAL = 3
_CONNECT_TIMEOUT = 3


def _get_compose_dir() -> str:
    if platform.system() == "Windows":
        return _COMPOSE_PATH_WINDOWS
    return _COMPOSE_PATH_LINUX


def _api_base_url() -> str:
    url = settings.LEGALMIND_API_URL or "http://localhost:8000/api/v1/"
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _ping_api() -> bool:
    try:
        resp = requests.get(_api_base_url(), timeout=_CONNECT_TIMEOUT)
        return resp.status_code < 500
    except Exception:
        return False


def _run_docker_compose_up(compose_dir: str) -> bool:
    # Tenta docker compose (V2) e depois docker-compose (V1)
    for cmd in [["docker", "compose", "up", "-d"], ["docker-compose", "up", "-d"]]:
        try:
            result = subprocess.run(cmd, cwd=compose_dir, capture_output=True, text=True)
            if result.returncode == 0:
                if result.stderr.strip():
                    logger.debug(f"docker compose stderr:\n{result.stderr.strip()}")
                return True
            logger.warning(f"'{' '.join(cmd)}' falhou (exit {result.returncode}):\n{result.stderr.strip()}")
        except FileNotFoundError:
            continue
    logger.error("Nenhuma variante de docker-compose encontrada no PATH.")
    return False


def ensure_legalmind_running(verbose: bool = False) -> bool:
    """
    Garante que a API LegalMind esteja acessível.
    - Fast-path: se já responde, retorna True imediatamente.
    - Se não: dispara docker compose up -d e faz polling por até 90s.
    - verbose=True: logs INFO a cada tentativa (usar em main.py).
    - verbose=False: silencioso no fast-path (usar em integracao_legalmind.py).
    """
    if _ping_api():
        logger.debug("LegalMind API já está em execução (fast-path).")
        return True

    compose_dir = _get_compose_dir()
    logger.info(f"LegalMind API não responde. Iniciando containers em '{compose_dir}'...")

    if not _run_docker_compose_up(compose_dir):
        logger.error("Falha ao executar docker compose up.")
        return False

    logger.info(f"Containers iniciados. Aguardando API (máx. {_POLL_RETRIES * _POLL_INTERVAL}s)...")

    for attempt in range(1, _POLL_RETRIES + 1):
        time.sleep(_POLL_INTERVAL)
        if _ping_api():
            logger.info(f"LegalMind API pronta após {attempt * _POLL_INTERVAL}s.")
            return True
        if verbose or attempt % 5 == 0:
            elapsed = attempt * _POLL_INTERVAL
            remaining = (_POLL_RETRIES - attempt) * _POLL_INTERVAL
            logger.info(f"Aguardando LegalMind... {elapsed}s decorridos, timeout em {remaining}s.")

    logger.error(
        f"LegalMind API não respondeu após {_POLL_RETRIES * _POLL_INTERVAL}s. "
        "Verifique: docker compose logs api"
    )
    return False
