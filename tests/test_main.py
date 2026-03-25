import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Definir as enums ambientes cruciais antes da inicialização do app para os testes.
import os
os.environ["API_KEY"] = "test-api-key"
os.environ["EPROC_LOGIN"] = "test_user"
os.environ["EPROC_SENHA"] = "test_pass"

from src.main import app
from src.scripts.base import ScraperResult

client = TestClient(app)

def test_root_endpoint():
    """Testa se a raiz da API está retornando status 200 e boas-vindas."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Bem-vindo" in response.json()["message"]

def test_agendar_script_sem_auth():
    """Testa se acessar os endpoints protegidos sem chave levanta um 401."""
    response = client.post("/run/qualquer_script")
    assert response.status_code == 401
    assert "API Key inválida ou não fornecida" in response.json()["detail"]

@patch("src.main.execute_script", new_callable=AsyncMock)
def test_agendar_script_com_auth(mock_execute):
    """Testa se a chamada bem-sucedida do script retorna os dados corretamente usando mock."""
    mock_execute.return_value = ScraperResult(
        success=True,
        message="Script finalizado com sucesso",
        execution_time=1.5
    )
    headers = {"X-API-Key": "test-api-key"}
    response = client.post("/run/test_script", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Script finalizado com sucesso"
    assert mock_execute.call_count == 1
    
def test_agendar_script_nao_encontrado():
    """Testa se passar um script inválido retorna corretamente um erro 404."""
    headers = {"X-API-Key": "test-api-key"}
    
    # Executamos o controller, que deve explodir a exceção lá dentro
    response = client.post("/run/script_inexistente", headers=headers)
    assert response.status_code == 404
    assert str("Não encontrado" in response.json().get("detail", "")) or str("não encontrado" in response.json().get("detail", ""))
