from src.scripts.loc_base import LocBaseScraper

class LocPeticaoInicial(LocBaseScraper):
    LOCATOR_NAME = "PETIÇÃO INICIAL"
    OUTPUT_FILENAME = "processos_peticao_inicial.csv"
