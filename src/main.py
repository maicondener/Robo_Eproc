"""
Módulo principal para o Robô Eproc TJTO.

Este módulo oferece duas formas de operação:
1. Como uma API web usando FastAPI para executar scripts de extração de dados.
2. Como um utilitário de linha de comando (CLI) para execuções locais.

Ele é responsável por carregar dinamicamente e executar scripts localizados 
na pasta `src/scripts`, utilizando o Playwright para automação web.
"""
import asyncio
import argparse
import importlib.util
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright

# Carrega as variáveis de ambiente do arquivo .env no início do script
load_dotenv()


# --- LÓGICA CENTRAL DE EXECUÇÃO ---

async def execute_script(script_name: str, headless: bool = True) -> dict:
    """
    Carrega e executa dinamicamente um script de automação da pasta 'scripts'.

    A função valida a existência do script, o carrega como um módulo Python,
    inicia uma instância do Playwright com um navegador Chromium e chama a função
    `run(page)` dentro do script, passando a página do navegador como argumento.

    Args:
        script_name: O nome do arquivo do script (sem a extensão .py).
        headless: Se True, o navegador será executado em modo headless (sem interface gráfica).
                  Se False, a janela do navegador será exibida.

    Returns:
        Um dicionário contendo o resultado retornado pela função `run` do script.

    Raises:
        FileNotFoundError: Se o arquivo do script não for encontrado no diretório 'src/scripts'.
        ImportError: Se houver um problema ao carregar o módulo do script.
        AttributeError: Se o script não contiver uma função `run`.
    """
    script_path = Path("src/scripts") / f"{script_name}.py"

    # Validação de segurança para garantir que o script está na pasta correta
    if not script_path.is_file() or not str(script_path.resolve()).startswith(str(Path("src/scripts").resolve())):
        raise FileNotFoundError(f"Script '{script_name}.py' não encontrado ou acesso negado.")

    # Carregar o módulo dinamicamente
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível criar a especificação para o script '{script_name}.py'.")
    
    script_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script_module)

    if not hasattr(script_module, "run"):
        raise AttributeError(f"O script '{script_name}.py' não possui uma função 'run'.")

    # Iniciar o Playwright e executar o script
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        try:
            print(f"Executando script '{script_name}'...")
            result = await script_module.run(page)
            print("Execução concluída com sucesso.")
            return result
        finally:
            await browser.close()

# --- MODO API (FastAPI) ---

app = FastAPI(
    title="Robô Eproc TJTO",
    description="API para automatizar a extração de dados do sistema eproc do TJTO. Permite a execução remota de scripts de automação.",
    version="0.1.0",
    contact={
        "name": "Desenvolvedor",
        "url": "http://github.com/seu-usuario",
        "email": "seu-email@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint raiz da API.
    
    Retorna uma mensagem de boas-vindas e verifica se as variáveis de ambiente essenciais estão carregadas.
    """
    # Exemplo de como acessar as variáveis de ambiente (verificação)
    login = os.getenv("EPROC_LOGIN")
    senha = os.getenv("EPROC_SENHA")
    
    if not login or not senha:
        print("AVISO: Variáveis de ambiente EPROC_LOGIN e/ou EPROC_SENHA não definidas.")
        print("Certifique-se de que o arquivo .env existe na raiz do projeto e tem os valores corretos.")
        
    return {"message": "Bem-vindo à API do Robô Eproc TJTO!"}

@app.post("/run/{script_name}", tags=["Scraper"])
async def run_script_endpoint(script_name: str):
    """
    Endpoint da API para acionar a execução de um script de extração.

    Recebe o nome de um script, o executa em modo não-headless (navegador visível)
    e retorna o resultado da extração.

    Args:
        script_name: O nome do script a ser executado (localizado em `src/scripts`).

    Returns:
        O resultado da execução do script em formato JSON.

    Raises:
        HTTPException(404): Se o script não for encontrado ou for inválido.
        HTTPException(500): Para erros inesperados durante a execução do script.
    """
    try:
        # No modo API, o padrão é mostrar o navegador para facilitar a depuração.
        result = await execute_script(script_name, headless=False)
        return result
    except (FileNotFoundError, ImportError, AttributeError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao executar o script: {e}")


# --- MODO LINHA DE COMANDO (CLI) ---

def main_cli():
    """
    Ponto de entrada para a execução do robô via linha de comando.

    Analisa os argumentos da CLI para obter o nome do script e as opções de execução
    (como exibir ou não o navegador) e, em seguida, chama a função `execute_script`.
    """
    parser = argparse.ArgumentParser(
        description="Robô Eproc TJTO - Executor de Scripts via Linha de Comando.",
        epilog="Exemplo de uso: python src/main.py --script exemplo_extracao --show-browser"
    )
    parser.add_argument(
        "--script",
        type=str,
        required=True,
        help="Nome do script a ser executado (sem a extensão .py).",
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="Exibe a janela do navegador durante a execução. O padrão é rodar em background (headless).",
    )
    args = parser.parse_args()

    # O modo headless é o padrão, a menos que a flag --show-browser seja passada.
    is_headless = not args.show_browser
    
    try:
        result = asyncio.run(execute_script(args.script, headless=is_headless))
        print("\n--- Resultado da Execução ---")
        print(result)
        print("-----------------------------")
    except (FileNotFoundError, ImportError, AttributeError) as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERRO Inesperado: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Demonstração de acesso às variáveis de ambiente no modo CLI
    login = os.getenv("EPROC_LOGIN")
    senha = os.getenv("EPROC_SENHA")

    print("--- Verificação de Variáveis de Ambiente ---")
    if login and senha:
        # Por segurança, nunca imprima a senha em logs de produção
        print(f"Login EPROC: {login}")
        print(f"Senha EPROC: {'*' * len(senha)}")
        print("-> Variáveis de ambiente carregadas com sucesso.")
    else:
        print("AVISO: EPROC_LOGIN e/ou EPROC_SENHA não foram encontradas.")
        print("-> Certifique-se de criar e preencher o arquivo .env na raiz do projeto.")
    print("------------------------------------------\n")
    
    main_cli()
