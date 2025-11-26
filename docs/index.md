# Bem-vindo ao Robô de Extração Eproc

O **Robô de Extração Eproc** é uma ferramenta de automação desenvolvida para extrair dados e realizar tarefas no sistema Eproc. A solução é flexível, permitindo a execução de scripts tanto via uma API web quanto por uma interface de linha de comando (CLI).

## ✨ Principais Características

- **Dupla Interface:** Execute automações através de uma API RESTful (FastAPI) ou diretamente no terminal.
- **Gerenciamento Seguro de Credenciais:** Utiliza arquivos `.env` validados pelo Pydantic para gerenciar configurações.
- **Automação Moderna:** Construído com [Playwright](https://playwright.dev/python/) para uma automação web robusta.
- **Logs Estruturados:** Sistema de logs com rotação de arquivos e saída colorida no console (Loguru).
- **Extensível:** Arquitetura baseada em classes (`BaseScraper`) para fácil criação de novos scripts.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Framework API:** FastAPI
- **Automação Web:** Playwright
- **Configuração:** Pydantic Settings
- **Logs:** Loguru
- **Servidor ASGI:** Uvicorn

## ⚙️ Configuração do Ambiente

Siga os passos abaixo para configurar o ambiente de desenvolvimento.

### 1. Pré-requisitos
- [Python](https://www.python.org/downloads/) (versão 3.10 ou superior)
- [Git](https://git-scm.com/downloads/)

### 2. Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd Robo_Eproc
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Crie o ambiente
    python -m venv .venv

    # Ative (Windows)
    .venv\Scripts\activate
    
    # Ative (macOS/Linux)
    source .venv/bin/activate
    ```

3.  **Crie o arquivo de credenciais:**
    Copie o arquivo de exemplo `.env.example` para `.env` e preencha com suas credenciais.
    ```bash
    cp .env.example .env
    ```
    
    Edite o arquivo `.env`:
    ```ini
    # .env
    EPROC_LOGIN="seu_login_aqui"
    EPROC_SENHA="sua_senha_aqui"
    
    # Opcionais (valores padrão)
    EPROC_URL="https://eproc1.tjto.jus.br/eprocV2_prod_1grau/"
    HEADLESS=True
    LOG_LEVEL="INFO"
    ```

4.  **Instale as dependências e os navegadores:**
    ```bash
    # Instala as bibliotecas Python
    pip install -r requirements.txt

    # Baixa os navegadores para o Playwright
    playwright install
    ```

## 🚀 Como Usar

### 1. Via Linha de Comando (CLI)

Ideal para execuções pontuais e testes. Execute o script principal usando o módulo `src.main`.

**Scripts Disponíveis:**

- **`exemplo_extracao`**: Um tutorial interativo que demonstra como usar o Playwright (navegação, seletores, ações). Ótimo para aprendizado.
- **`loc_peticoes`**: Script para extração da lista de processos do localizador PETIÇÕES.

**Exemplos:**

- **Rodar o tutorial de exemplo:**
  ```bash
  python -m src.main --script exemplo_extracao --show-browser
  ```

- **Rodar a extração de petições:**
  ```bash
  python -m src.main --script loc_peticoes
  ```

### 2. Via API Web

A API permite integrar o robô a outros sistemas.

1.  **Inicie o servidor:**
    ```bash
    uvicorn src.main:app --reload
    ```
    O servidor estará disponível em `http://127.0.0.1:8000`.

2.  **Acesse a documentação:**
    Acesse [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) para ver a documentação interativa (Swagger UI).

3.  **Execute um script via API:**
    Faça uma requisição `POST` ao endpoint `/run/{script_name}`.

## 🤖 Adicionando Novos Scripts

1.  Crie um novo arquivo Python na pasta `src/scripts/` (ex: `meu_script.py`).
2.  Importe `BaseScraper` e `ScraperResult`.
3.  Crie uma classe que herde de `BaseScraper` e implemente o método `run`.

    ```python
    # src/scripts/meu_script.py
    from playwright.async_api import Page
    from src.scripts.base import BaseScraper, ScraperResult

    class MeuScript(BaseScraper):
        async def run(self, page: Page) -> ScraperResult:
            self.logger.info("Iniciando meu script...")
            
            # Navega para a URL configurada no .env
            await self.navigate_to_home(page)

            # ... sua lógica de automação ...
            title = await page.title()
            
            return ScraperResult(
                success=True,
                data={"titulo": title},
                message="Sucesso!"
            )
    ```
4.  Execute: `python -m src.main --script meu_script`

## 📁 Estrutura do Projeto

```
Robo_Eproc/
├── .venv/                # Ambiente virtual
├── docs/                 # Documentação (MkDocs)
├── logs/                 # Arquivos de log rotacionados
├── src/
│   ├── scripts/          # Scripts de automação
│   │   ├── base.py       # Classe BaseScraper
│   │   ├── exemplo_extracao.py # Tutorial Playwright
│   │   └── loc_peticoes.py     # Extração de Petições
│   ├── config.py         # Configurações (Pydantic)
│   ├── logger.py         # Configuração de Logs
│   └── main.py           # Ponto de entrada (API e CLI)
├── .env                  # Variáveis de ambiente (Ignorado pelo Git)
├── .env.example          # Modelo de variáveis de ambiente
├── mkdocs.yml            # Configuração MkDocs
├── README.md             # Este arquivo
└── requirements.txt      # Dependências
```
