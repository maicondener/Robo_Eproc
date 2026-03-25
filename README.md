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
```bash
python -m src.main --script loc_urgente
```

**Extrair Relatório de Processos Conclusos:**
```bash
python -m src.main --script relatorio_conclusos
```
Este script extrai a planilha, converte para JSON e envia diretamente para a API do LegalMind.

**Extrair Relatório de Alvarás Eletrônicos (Sincronização Google Drive):**
```bash
python -m src.main --script alvaras_eletronicos
```
Este script automatiza a extração de alvarás e sincroniza os dados diretamente com uma planilha no **Google Drive**, realizando o merge automático para evitar duplicidade.

**Modo debug (browser visível):**
```bash
python -m src.main --script loc_peticoes --show-browser
```

### 4. Integração LegalMind API

O robô agora está configurado para enviar os dados diretamente para o Core do sistema LegalMind, eliminando a necessidade de gestão manual de arquivos CSV.

**Para que a integração funcione:**
1.  Configure `LEGALMIND_API_URL` e `LEGALMIND_API_KEY` no `.env`.
2.  O robô **inicia automaticamente** o LegalMind Core via Docker se ele não estiver rodando.
    - Requer Docker instalado e o projeto LegalMind em `/mnt/c/LegalMind` (Linux/WSL) ou `C:\LegalMind` (Windows).
    - Para gerar o token: `docker exec -it legalmind_api python create_token.py`

### 5. Execução via API Web

Para rodar o robô como um serviço que pode ser acessado por outros sistemas:

```bash
uvicorn src.main:app --reload
```

O servidor estará disponível em `http://localhost:8000`.

**Executar um script via API (cURL):**
```bash
curl -X POST "http://localhost:8000/run/loc_peticoes" \
  -H "X-API-Key: sua_api_key_aqui"
```

**Documentação interativa:** Acesse `http://localhost:8000/docs` no navegador para testar os endpoints.

## ✨ Features

- ✅ **Integração Google Drive** — Sincronização automática de planilhas.
- ✅ **Estabilidade Headless** — Configuração automática de User-Agent e Viewport para evitar bloqueios 403.
- ✅ **Login Automático** com suporte a 2FA (TOTP).
- ✅ **Seleção de Perfil** automática.
- ✅ **Persistência de Sessão** (evita logins repetidos).
- ✅ **Paginação Automática** na extração de processos.
- ✅ **Exportação CSV/Excel** limpa e organizada.
- ✅ **LegalMind Auto-Startup** — inicia containers Docker automaticamente se necessário.
- ✅ **Modo API** (FastAPI) e **CLI**.