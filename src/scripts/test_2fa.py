from src.config import settings
import pyotp
import time

def test_totp():
    secret = settings.EPROC_2FA_SECRET
    
    if not secret:
        print("❌ ERRO: EPROC_2FA_SECRET não está configurado no .env")
        return

    print(f"ℹ️  Segredo configurado: {secret[:4]}...{secret[-4:]} (ocultado por segurança)")
    
    try:
        totp = pyotp.TOTP(secret)
        code = totp.now()
        print(f"\n✅ Código Gerado: {code}")
        print("Compare este código com o do seu aplicativo autenticador (Google/Microsoft Authenticator).")
        print("Eles devem ser iguais.")
        
    except Exception as e:
        print(f"\n❌ ERRO ao gerar código: {e}")
        print("Verifique se o segredo no .env está correto (sem espaços, formato Base32).")

if __name__ == "__main__":
    test_totp()
