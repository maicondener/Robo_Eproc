import pyotp
import time
import os
from datetime import datetime

# Tenta carregar do .env manualmente para garantir que não há processamento extra
from dotenv import load_dotenv
load_dotenv()

secret = os.getenv("EPROC_2FA_SECRET")

print("-" * 30)
print("DIAGNÓSTICO DE 2FA")
print("-" * 30)

print(f"Hora do Sistema (Local): {datetime.now()}")
print(f"Timestamp UTC: {int(time.time())}")

if not secret:
    print("ERRO: EPROC_2FA_SECRET não encontrado nas variáveis de ambiente.")
else:
    # Remove espaços em branco que possam ter sido copiados acidentalmente
    clean_secret = secret.replace(" ", "").strip()
    
    print(f"Secret Configurado (Oculto): {secret[:4]}...{secret[-4:]} (Tamanho: {len(secret)})")
    
    if len(secret) != len(clean_secret):
        print(f"AVISO: O secret contém espaços! (Original: {len(secret)} chars, Limpo: {len(clean_secret)} chars)")
        print("Tentando gerar código com secret LIMPO...")
        secret = clean_secret

    try:
        totp = pyotp.TOTP(secret)
        code = totp.now()
        print(f"Código Gerado Agora: {code}")
        print(f"Tempo Restante para este código: {totp.interval - (time.time() % totp.interval):.1f}s")
    except Exception as e:
        print(f"ERRO ao gerar código: {e}")

print("-" * 30)
print("Verifique se este código bate com o do seu aplicativo autenticador.")
print("-" * 30)
