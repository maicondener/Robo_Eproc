import requests
from typing import List
from src.logger import logger
from src.config import settings

def enviar_para_legalmind(processos: List[str], localizador: str = None):
    """
    Envia a lista de processos extraídos para a API do LegalMind Core,
    incluindo o nome do localizador como contexto.
    """
    if not settings.LEGALMIND_API_URL:
        logger.warning("LEGALMIND_API_URL não configurada. Pulando integração.")
        return False

    url = f"{settings.LEGALMIND_API_URL.rstrip('/')}/processos/importar"
    
    # Prepara o payload como uma lista de objetos
    payload = [
        {"numero_processo": p, "localizador": localizador}
        for p in processos
    ]
    
    try:
        logger.info(f"Enviando {len(processos)} processos (Localizador: {localizador}) para o LegalMind: {url}")
        
        response = requests.post(
            url, 
            json=payload,
            headers={"Authorization": settings.LEGALMIND_API_KEY or "Bearer valid_token"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Integração concluída: {result.get('importados')} novos processos importados.")
            return True
        else:
            logger.error(f"Falha na integração com LegalMind: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao conectar com a API do LegalMind: {e}")
        return False

def enviar_relatorio_concluso(items: List[dict]):
    """
    Envia os dados detalhados de um relatório de processos conclusos para o LegalMind.
    """
    if not settings.LEGALMIND_API_URL:
        logger.warning("LEGALMIND_API_URL não configurada. Pulando integração.")
        return False

    url = f"{settings.LEGALMIND_API_URL.rstrip('/')}/relatorios/conclusos"
    
    try:
        logger.info(f"Enviando relatório com {len(items)} itens para o LegalMind: {url}")
        
        response = requests.post(
            url, 
            json=items,
            headers={"Authorization": settings.LEGALMIND_API_KEY or "Bearer valid_token"},
            timeout=60
        )
        
        if response.status_code == 200:
            logger.info("Relatório integrado com sucesso ao LegalMind Core.")
            return True
        else:
            logger.error(f"Falha ao enviar relatório: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Erro na integração do relatório: {e}")
        return False
