# Bem-vindo ao Robô de Extração Eproc

O **Robô de Extração Eproc** é uma ferramenta de automação desenvolvida para extrair dados e realizar tarefas no sistema Eproc. A solução é flexível, permitindo a execução de scripts tanto via uma API web quanto por uma interface de linha de comando (CLI).

## ✨ Principais Características

- **Dupla Interface:** Execute automações através de uma API RESTful (FastAPI) ou diretamente no terminal.
- **Gerenciamento Seguro de Credenciais:** Utiliza arquivos `.env` para gerenciar login e senha de forma segura, sem expor dados sensíveis no código.
- **Automação Moderna:** Construído com [Playwright](https://playwright.dev/python/) para uma automação web robusta e confiável.
- **Extensível:** Facilmente expansível com novos scripts de automação para diferentes tarefas.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Framework API:** FastAPI
- **Automação Web:** Playwright
- **Servidor ASGI:** Uvicorn
- **Variáveis de Ambiente:** Python-Dotenv

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
    Crie um arquivo chamado `.env` na raiz do projeto, copiando o modelo abaixo. Este arquivo guardará suas credenciais de forma segura.
    ```ini
    # .env
    EPROC_LOGIN="seu_login_aqui"
    EPROC_SENHA="sua_senha_aqui"
    ```
    > **Importante:** O arquivo `.env` já está no `.gitignore`, então suas credenciais nunca serão enviadas para o repositório.

4.  **Instale as dependências e os navegadores:**
    Com o ambiente ativado, execute os dois comandos abaixo:
    ```bash
    # Instala as bibliotecas Python
    pip install -r requirements.txt

    # Baixa os navegadores para o Playwright
    playwright install
    ```

## 🚀 Como Usar

### 1. Via Linha de Comando (CLI)

Ideal para execuções pontuais e testes.

- Execute o script principal `main.py` com o argumento `--script`, passando o nome do arquivo (sem `.py`) que está na pasta `src/scripts/`.

- **Exemplo (executando `exemplo_extracao.py`):**
  ```bash
  python src/main.py --script exemplo_extracao
  ```

- **Para visualizar o navegador durante a execução**, adicione a flag `--show-browser`:
  ```bash
  python src/main.py --script exemplo_extracao --show-browser
  ```

### 2. Via API Web

A API permite integrar o robô a outros sistemas.

1.  **Inicie o servidor:**
    ```bash
    uvicorn src.main:app --reload
    ```
    O servidor estará disponível em `http://127.0.0.1:8000`.

2.  **Acesse a documentação:**
    Acesse [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) para ver a documentação interativa do Swagger UI.

3.  **Execute um script via API:**
    Use uma ferramenta como `curl` ou o próprio Swagger UI para fazer uma requisição `POST` ao endpoint `/run/{script_name}`.

    - **Exemplo com `curl`:**
      ```bash
      curl -X POST http://127.0.0.1:8000/run/exemplo_extracao -H "accept: application/json"
      ```

## 🤖 Adicionando Novos Scripts

1.  Crie um novo arquivo Python na pasta `src/scripts/`.
2.  Dentro do arquivo, defina uma função assíncrona chamada `run`, que recebe um objeto `page` do Playwright como argumento.
    ```python
    # src/scripts/meu_novo_script.py
    import os
    from playwright.async_api import Page, expect

    async def run(page: Page) -> dict:
        # Acesse as credenciais de forma segura
        login = os.getenv("EPROC_LOGIN")
        senha = os.getenv("EPROC_SENHA")

        # ... seu código de automação aqui ...
        await page.goto("https://eproc.tjto.jus.br/")
        # Exemplo: preencher login e senha
        
        return {"status": "sucesso", "dados": "..."}
    ```
3.  Execute seu novo script pela CLI ou API usando o nome do arquivo (ex: `meu_novo_script`).
