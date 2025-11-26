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
import inspect
import sys
import os
from pathlib import Path
from typing import Type

from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright

from src.config import settings
from src.logger import logger
from src.scripts.base import BaseScraper, ScraperResult

# --- LÓGICA CENTRAL DE EXECUÇÃO ---

def load_scraper_class(script_name: str) -> Type[BaseScraper]:
    """
    Carrega dinamicamente a classe do scraper a partir do nome do script.
    """
    script_path = Path("src/scripts") / f"{script_name}.py"

    # Validação de segurança
    if not script_path.is_file() or not str(script_path.resolve()).startswith(str(Path("src/scripts").resolve())):
        raise FileNotFoundError(f"Script '{script_name}.py' não encontrado ou acesso negado.")

    # Carregar o módulo
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível criar a especificação para o script '{script_name}.py'.")
    
    script_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script_module)

    # Encontrar a classe que herda de BaseScraper
    for name, obj in inspect.getmembers(script_module):
        if inspect.isclass(obj) and issubclass(obj, BaseScraper) and obj is not BaseScraper:
            return obj
    
    raise AttributeError(f"Nenhuma subclasse de BaseScraper encontrada em '{script_name}.py'.")

async def execute_script(script_name: str, headless: bool = True) -> ScraperResult:
    """
    Executa o script solicitado.
    """
    try:
        ScraperClass = load_scraper_class(script_name)
        scraper = ScraperClass()
    except (FileNotFoundError, ImportError, AttributeError) as e:
        logger.error(f"Erro ao carregar script: {e}")
        raise e

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            channel=settings.BROWSER_CHANNEL
        )
        # Configura o contexto do navegador (cookies, sessão, etc)
        # Tenta carregar o estado da sessão se existir
        storage_state_path = "state.json"
        if os.path.exists(storage_state_path):
            logger.info(f"Carregando sessão existente de '{storage_state_path}'")
            context = await browser.new_context(storage_state=storage_state_path)
        else:
            logger.info("Iniciando nova sessão (sem estado salvo)")
            context = await browser.new_context()
            
        page = await context.new_page()
        try:
            logger.info(f"Iniciando execução do script '{script_name}'...")
            result = await scraper.run(page)
            logger.info(f"Execução concluída. Sucesso: {result.success}")
            return result
        except Exception as e:
            logger.exception(f"Erro crítico durante a execução do script '{script_name}': {e}")
            return ScraperResult(
                success=False,
                message=f"Erro crítico: {str(e)}",
                execution_time=0.0
            )
        finally:
            await browser.close()

# --- MODO API (FastAPI) ---

app = FastAPI(
    title="Robô Eproc TJTO",
    description="API para automatizar a extração de dados do sistema eproc do TJTO.",
    version="0.2.0",
)

@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint raiz da API."""
    if not settings.EPROC_LOGIN or not settings.EPROC_SENHA:
        logger.warning("Credenciais não configuradas no .env")
        
    return {"message": "Bem-vindo à API do Robô Eproc TJTO!", "env": settings.model_dump(include={"LOG_LEVEL", "HEADLESS"})}

@app.post("/run/{script_name}", response_model=ScraperResult, tags=["Scraper"])
async def run_script_endpoint(script_name: str):
    """
    Endpoint da API para acionar a execução de um script de extração.
    """
    try:
        # Na API, usamos a configuração global para headless, mas podemos forçar False para debug se necessário
        # Aqui vamos respeitar a config ou forçar False se for debug local
        result = await execute_script(script_name, headless=settings.HEADLESS)
        return result
    except (FileNotFoundError, ImportError, AttributeError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {e}")


# --- MODO LINHA DE COMANDO (CLI) ---

def main_cli():
    """
    Ponto de entrada para a execução do robô via linha de comando.
    """
    parser = argparse.ArgumentParser(
        description="Robô Eproc TJTO - Executor de Scripts via Linha de Comando."
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
        help="Exibe a janela do navegador durante a execução.",
    )
    args = parser.parse_args()

    # Prioridade: Argumento CLI > Configuração .env
    is_headless = not args.show_browser if args.show_browser else settings.HEADLESS
    
    try:
        result = asyncio.run(execute_script(args.script, headless=is_headless))
        print("\n--- Resultado da Execução ---")
        print(result.model_dump_json(indent=2))
        print("-----------------------------")
    except Exception as e:
        logger.error(f"Erro fatal na CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main_cli()
