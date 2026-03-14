import pyotp
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
secret = os.getenv("EPROC_2FA_SECRET")

if not secret:
    print("ERRO: Configure EPROC_2FA_SECRET no .env primeiro!")
    exit(1)

clean_secret = secret.replace(" ", "").strip()
totp = pyotp.TOTP(clean_secret)

current_time = time.time()
print(f"Hora do Sistema: {datetime.now()}")
print(f"Timestamp: {current_time}")

print("\n--- ESCANEANDO DRIFT TEMPORAL ---")
print("Tentando encontrar um código válido variando o tempo...")

# Tenta offsets de horas completas (fuso horário)
found_offsets = []

for hour_offset in range(-12, 13):
    offset_seconds = hour_offset * 3600
    test_time = current_time + offset_seconds
    code = totp.at(test_time)
    
    # Imprime apenas alguns para referência ou se o usuário reconhecer
    time_str = (datetime.now() + timedelta(hours=hour_offset)).strftime("%H:%M:%S")
    print(f"Offset {hour_offset:+}h ({time_str}): {code}")

print("\n--- ESCANEANDO MINUTOS (Janela de 30min) ---")
# Tenta cada minuto nos próximos 30 min e passados
for minute_offset in range(-30, 31):
    if minute_offset == 0: continue
    offset_seconds = minute_offset * 60
    test_time = current_time + offset_seconds
    code = totp.at(test_time)
    # print(f"Offset {minute_offset:+}m: {code}") 
    # Não vamos imprimir tudo para não poluir, mas a ideia é se o usuário tivesse dito qual é o código correto, poderiamos buscar.

print("\nSe você puder me dizer QUAL é o código correto que aparece no seu app agora, eu posso encontrar o offset exato!")
