import csv
import os
from typing import List
from src.logger import logger

def clean_process_number(process_number: str) -> str:
    """
    Remove caracteres não numéricos do número do processo.
    Ex: '0002508-62.2018.8.27.2716' -> '00025086220188272716'
    """
    return "".join(filter(str.isdigit, process_number))

def save_to_csv(processos: List[str], filename: str = "processos.csv", output_dir: str = "data"):
    """
    Salva a lista de processos em um arquivo CSV, limpando a pontuação.
    
    Args:
        processos: Lista de strings com os números dos processos.
        filename: Nome do arquivo de saída.
        output_dir: Diretório onde o arquivo será salvo.
    """
    try:
        # Cria o diretório se não existir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Diretório '{output_dir}' criado.")

        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # Escreve o cabeçalho
            writer.writerow(["numero_processo"])
            
            count = 0
            for proc in processos:
                clean_proc = clean_process_number(proc)
                if clean_proc:
                    writer.writerow([clean_proc])
                    count += 1
                    
        logger.info(f"Arquivo CSV salvo com sucesso em: {filepath} ({count} registros)")
        return filepath
    except Exception as e:
        logger.error(f"Erro ao salvar CSV: {e}")
        return None
