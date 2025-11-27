from src.scripts.loc_base import LocBaseScraper

class LocUrgente(LocBaseScraper):
    LOCATOR_NAME = "URGENTE"
    OUTPUT_FILENAME = "processos_urgente.csv"
