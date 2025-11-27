from src.scripts.loc_base import LocBaseScraper

class LocPeticoes(LocBaseScraper):
    LOCATOR_NAME = "PETIÇÃO"
    OUTPUT_FILENAME = "processos_peticao.csv"

