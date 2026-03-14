import pyotp
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
secret = os.getenv("EPROC_2FA_SECRET")

if not secret:
    print("ERRO: Configure EPROC_2FA_SECRET no .env primeiro!")
    exit(1)

clean_secret = secret.replace(" ", "").strip()
print(f"Testando variantes para o secret: {clean_secret[:4]}...{clean_secret[-4:]}")
print(f"Hora atual: {datetime.now()}")

print("\n--- VARIANTES PADRÃO ---")
# Padrão: 30s, 6 digitos, SHA1
totp_std = pyotp.TOTP(clean_secret)
print(f"1. Padrão (30s, 6d, SHA1): {totp_std.now()}")

# 60s
totp_60 = pyotp.TOTP(clean_secret, interval=60)
print(f"2. Intervalo 60s: {totp_60.now()}")

# 8 Digitos
totp_8 = pyotp.TOTP(clean_secret, digits=8)
print(f"3. 8 Digitos: {totp_8.now()}")

# SHA256
import hashlib
totp_sha256 = pyotp.TOTP(clean_secret, digest=hashlib.sha256)
print(f"4. SHA256: {totp_sha256.now()}")

# SHA512
totp_sha512 = pyotp.TOTP(clean_secret, digest=hashlib.sha512)
print(f"5. SHA512: {totp_sha512.now()}")


print("\n--- TESTE DE DRIFT (Padrão 30s/6d) ---")
# Testa códigos anteriores e futuros para ver se é problema de relógio
totp = pyotp.TOTP(clean_secret)
print(f"Agora (-30s): {totp.at(time.time() - 30)}")
print(f"Agora (Atual): {totp.now()}")
print(f"Agora (+30s): {totp.at(time.time() + 30)}")

print("\nVerifique qual dessas opções bate com o seu aplicativo autenticador.")
