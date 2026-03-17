# Robô de Extração Eproc 🤖

Ferramenta de automação para extração de dados do sistema Eproc (TJTO), com suporte a **2FA**, **Seleção de Perfil** e **API Web**.

## 📚 Documentação Completa

A documentação detalhada do projeto está disponível na pasta `docs/`.

- **[Guia de Instalação e Configuração](docs/setup.md)**
- **[Guia de Uso e Scripts](docs/usage.md)**
- **[Guia de Desenvolvimento](docs/development.md)**

## 🚀 Quick Start

### 1. Instalação

```bash
git clone <URL_REPO>
cd Robo_Eproc
python -m venv .venv
# Ative o venv (.venv\Scripts\activate no Windows)
pip install -r requirements.txt
playwright install
```

### 2. Configuração

Copie `.env.example` para `.env` e configure suas credenciais:

```ini
EPROC_LOGIN="seu_usuario"
EPROC_SENHA="sua_senha"
EPROC_2FA_SECRET="SUACHAVE2FA" # Opcional
EPROC_PERFIL="DIRETOR DE SECRETARIA" # Opcional

# Integração LegalMind Core
LEGALMIND_API_URL="http://localhost:8000/api/v1/"
LEGALMIND_API_KEY="Bearer ey..." # Gerado via `docker exec -it legalmind_api python create_token.py`
```

### 3. Execução

**Extrair processos do localizador "PETIÇÃO":**
```bash
python -m src.main --script loc_peticoes
```

**Extrair processos do localizador "PETIÇÃO INICIAL":**
```bash
python -m src.main --script loc_peticao_inicial
```

**Extrair processos do localizador "URGENTE":**
**Extrair Relatório de Processos Conclusos:**
```bash
python -m src.scripts.relatorio_conclusos
```
Este script extrai a planilha, converte para JSON e envia diretamente para a API do LegalMind.

### 4. Integração LegalMind API

O robô agora está configurado para enviar os dados diretamente para o Core do sistema LegalMind, eliminando a necessidade de gestão manual de arquivos CSV.

**Para que a integração funcione:**
1.  O **LegalMind Core** deve estar rodando (`docker-compose up`).
2.  Você deve gerar um token de autenticação no LegalMind (`create_token.py`) e adicioná-lo ao `.env` deste robô.

## ✨ Features

- ✅ **Login Automático** com suporte a 2FA (TOTP).
- ✅ **Seleção de Perfil** automática.
- ✅ **Persistência de Sessão** (evita logins repetidos).
- ✅ **Paginação Automática** na extração de processos.
- ✅ **Exportação CSV** limpa e organizada.
- ✅ **Modo API** (FastAPI) e **CLI**.