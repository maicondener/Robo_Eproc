# Robô Eproc TJTO

O **Robô Eproc TJTO** é uma ferramenta de automação (RPA) desenvolvida em Python para extração de dados de processos judiciais no sistema Eproc do Tribunal de Justiça do Estado do Tocantins. Ele utiliza Web Scraping assíncrono avançado através do Playwright.

## Funcionalidades Principais

- **Pesquisa e Extração em Localizadores**: Varre localizadores específicos no Eproc (ex: Petição Inicial, Petições, Urgente) e extrai os números dos processos através de expressões regulares.
- **Relatório de Processos Conclusos**: Emite, faz o download do relatório CSV, processa as datas e envia um pacote estruturado para integração.
- **Integração LegalMind**: Os dados extraídos são enviados via API de forma automática para o core do *LegalMind*.
- **Modos de Execução**: 
  - API REST HTTP usando **FastAPI**.
  - Interface de Linha de Comando (CLI).

## Tecnologias e Ferramentas

- Python 3.12+
- [Playwright](https://playwright.dev/python/) (Automação de Browser Assíncrona)
- [FastAPI](https://fastapi.tiangolo.com/) (API Framework web)
- [Pandas](https://pandas.pydata.org/) (Manipulação de dados CSV e análise)
- pydantic-settings (Validação de variáveis de ambiente)

## Requisitos

- Python instalado.
- O gerenciador de pacotes configurado (pip/poetry).
- Instalação dos navegadores do Playwright.

## Instalação e Configuração

1. Clone o repositório.
2. Crie e ative um ambiente virtual (ex: `python -m venv venv`, `venv\Scripts\activate`).
3. Instale as dependências: `pip install -r requirements.txt`.
4. Instale o(s) navegador(es) do Playwright:
   ```bash
   playwright install chromium
   ```

### Variáveis de Ambiente (`.env`)

Crie um arquivo `.env` na raiz do seu projeto baseando-se nas seguintes configurações necessárias:

```ini
# Configurações do Eproc
EPROC_LOGIN=seu_usuario
EPROC_SENHA=sua_senha
EPROC_URL=https://eproc1.tjto.jus.br/eprocV2_prod_1grau/

# API Robô (Para execução via FastAPI)
API_KEY=API-KEY-SUPER-SECRETA

# Integração LegalMind
LEGALMIND_API_URL=https://api.legalmind.com.br
LEGALMIND_API_KEY=Bearer SUA-CHAVE

# Headless mode (Mostrar ou ocultar o navegador, 'True' para ocultar)
HEADLESS=True
```

## Modos de Execução

### MODO CLI (Linha de Comando)
Ideal para testes no terminal, execuções locais assistidas ou CRON.

```bash
# Executa a extração do localizador "Petição Inicial" de forma oculta (headless)
python main.py --script loc_peticao_inicial

# Executa exibindo o navegador
python main.py --script loc_peticao_inicial --show-browser

# Relatório de Conclusos
python main.py --script eproc_concluso
```

### MODO API (FastAPI)
Inicia um servidor web pronto para receber triggers externos (via POST). Ideal para fluxos remotos programados, via webhook ou plataformas cloud.

1. Inicie o servidor:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
2. Realize chamadas autenticadas na API (usando o Header `X-API-Key`):
   ```bash
   curl -X POST "http://localhost:8000/run/loc_peticao_inicial" -H "X-API-Key: API-KEY-SUPER-SECRETA"
   ```
3. A documentação do Swagger da API estará disponível acessando via navegador `http://localhost:8000/docs`.
