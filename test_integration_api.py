import requests
import json

# Configurações do Teste
LEGALMIND_URL = "http://localhost:8000/api/v1/processos/importar"
TOKEN = "valid_token" # Token mock aceito pelo backend conforme backend/app/api/deps.py

def test_batch_import():
    print(f"--- Iniciando Teste de Integração ---")
    print(f"Alvo: {LEGALMIND_URL}")
    
    # Payload simulando o que o Robo Eproc envia
    payload = [
        {
            "numero_processo": "0001234-56.2024.8.27.2700",
            "localizador": "URGENTE"
        },
        {
            "numero_processo": "0009876-12.2023.8.27.2706",
            "localizador": "PETIÇÃO INICIAL"
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(LEGALMIND_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("✅ Sucesso!")
            print(f"Resposta da API: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Falha no teste: Status {response.status_code}")
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    test_batch_import()
