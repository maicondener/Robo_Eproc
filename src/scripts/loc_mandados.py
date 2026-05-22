from src.scripts.loc_base import LocBaseScraper


class LocMandados(LocBaseScraper):
    """
    Extrator de processos para o localizador MANDADOS - CITAÇÃO/INTIMAÇÃO ELETRÔNICA.
    Herda toda a lógica de navegação, extração de Excel e gravação em planilha do Google Sheets.
    """

    LOCATOR_NAME = 'MANDADOS - CITAÇÃO/INTIMAÇÃO ELETRÔNICA'
