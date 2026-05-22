import pyotp
from src.logger import logger
from src.config import settings

def testar_2fa():
    # Tenta obter a chave secreta das configurações
    secret = getattr(settings, 'EPROC_2FA_SECRET', None)
    
    if not secret:
        logger.error('A variável EPROC_2FA_SECRET não foi configurada no arquivo .env')
        return
        
    try:
        totp = pyotp.TOTP(secret.strip())
        logger.info(f'Código 2FA gerado com sucesso: {totp.now()}')
    except Exception as e:
        logger.error(f'Erro ao gerar código 2FA. Verifique sua chave secreta: {e}')

if __name__ == '__main__':
    testar_2fa()