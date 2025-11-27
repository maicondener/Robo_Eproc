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

## ✨ Features

- ✅ **Login Automático** com suporte a 2FA (TOTP).
- ✅ **Seleção de Perfil** automática.
- ✅ **Persistência de Sessão** (evita logins repetidos).
- ✅ **Paginação Automática** na extração de processos.
- ✅ **Exportação CSV** limpa e organizada.
- ✅ **Modo API** (FastAPI) e **CLI**.