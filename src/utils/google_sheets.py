import os
import re
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from loguru import logger

from src.config import settings


def get_sheets_service():
    """
    Autentica e retorna o serviço do Google Sheets usando Service Account.
    """
    if not settings.GOOGLE_APPLICATION_CREDENTIALS or not os.path.exists(
        settings.GOOGLE_APPLICATION_CREDENTIALS
    ):
        logger.warning(
            f'Credenciais do Google Sheets não encontradas no caminho: {settings.GOOGLE_APPLICATION_CREDENTIALS}'
        )
        return None

    try:
        # Define os escopos necessários para acessar planilhas e o drive
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
        ]
        creds = Credentials.from_service_account_file(
            settings.GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES
        )
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        logger.error(f'Erro ao autenticar no Google Sheets API: {e}')
        return None


def normalizar_data_br(data_str: str) -> str:
    """
    Normaliza strings de data vindas do eproc ou do Google Sheets para o padrão
    brasileiro com hífen separador 'DD/MM/AAAA - HH:MM:SS' para evitar que o Sheets
    trunque as horas se a coluna for formatada como data simples.
    Se não houver horas, adiciona ' - 00:00:00'.
    Suporta formatos como:
    - '18/05/2026 13:55:07'
    - '18/05/2026 - 13:55:07'
    - '18/05/2026'
    - '2026-05-18 13:55:07'
    - '2026-05-18'
    """
    if not data_str:
        return ''

    data_str = data_str.strip()

    # 1. Tentar casar padrão com hífen separador: DD/MM/AAAA - HH:MM:SS
    match_br_hiphen = re.match(r'^(\d{2})/(\d{2})/(\d{4})\s*-\s*(\d{2}):(\d{2}):(\d{2})$', data_str)
    if match_br_hiphen:
        g = match_br_hiphen.groups()
        return f'{g[0]}/{g[1]}/{g[2]} - {g[3]}:{g[4]}:{g[5]}'

    # 2. Tentar casar padrão BR completo: DD/MM/AAAA HH:MM:SS
    match_br_full = re.match(r'^(\d{2})/(\d{2})/(\d{4})\s+(\d{2}):(\d{2}):(\d{2})$', data_str)
    if match_br_full:
        g = match_br_full.groups()
        return f'{g[0]}/{g[1]}/{g[2]} - {g[3]}:{g[4]}:{g[5]}'

    # 3. Tentar casar padrão BR sem hora: DD/MM/AAAA
    match_br_date = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', data_str)
    if match_br_date:
        return f'{data_str} - 00:00:00'

    # 4. Tentar fazer o parse de formatos ISO (ex: vindo do Sheets ou APIs)
    try:
        data_clean = data_str.replace('T', ' ').split('.')[0]
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                dt = datetime.strptime(data_clean, fmt)
                return dt.strftime('%d/%m/%Y - %H:%M:%S')
            except ValueError:
                continue
    except Exception:
        pass

    return data_str


def salvar_processos_no_sheets(spreadsheet_id: str, dados_processos: list[dict]) -> list[str]:
    """
    Mapeia os cabeçalhos 'Processo' and 'Data' na planilha do Google Sheets,
    verifica duplicidade com base na chave composta (Processo, Data_Com_Hora)
    e insere em lote os registros inéditos para capturar múltiplos eventos no mesmo dia.

    Retorna a lista de números de processos inéditos adicionados nesta execução.
    """
    if not dados_processos:
        logger.info('Nenhum processo enviado para salvar no Google Sheets.')
        return []

    service = get_sheets_service()
    if not service:
        logger.error('Serviço do Google Sheets indisponível. A gravação será ignorada.')
        return []

    try:
        # 1. Identificar cabeçalhos na primeira linha da planilha (primeira aba ativa)
        logger.info('Lendo cabeçalhos da planilha do Google Sheets...')
        result_header = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range='A1:Z1')
            .execute()
        )

        rows_header = result_header.get('values', [])

        idx_processo = -1
        idx_data = -1

        if not rows_header or not rows_header[0]:
            # Planilha vazia: inicializa cabeçalho padrão
            logger.info('Planilha vazia. Inicializando cabeçalho padrão ["Processo", "Data"]')
            body_header = {'values': [['Processo', 'Data']]}
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='A1:B1',
                valueInputOption='USER_ENTERED',
                body=body_header,
            ).execute()
            idx_processo = 0
            idx_data = 1
        else:
            headers = [h.strip().lower() for h in rows_header[0]]

            # Busca de forma flexível por cabeçalhos que contenham 'processo' ou 'pocesso'
            for i, h in enumerate(headers):
                if 'processo' in h or 'pocesso' in h:
                    idx_processo = i
                    break

            # Busca por cabeçalhos que contenham 'data'
            for i, h in enumerate(headers):
                if 'data' in h:
                    idx_data = i
                    break

            # Fallbacks caso algum cabeçalho essencial não tenha sido identificado
            if idx_processo == -1:
                logger.warning(
                    'Cabeçalho de Processo não identificado. Adotando coluna A (index 0).'
                )
                idx_processo = 0
            if idx_data == -1:
                logger.warning('Cabeçalho de Data não identificado. Adotando coluna B (index 1).')
                idx_data = 1

        logger.info(
            f'Mapeamento de colunas no Sheets: Processo -> índice {idx_processo}, Data -> índice {idx_data}'
        )

        # 2. Ler todos os dados existentes para desduplicação histórica
        logger.info('Buscando dados existentes na planilha do Google Sheets...')
        # Lê uma faixa ampla da planilha
        result_data = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range='A2:Z100000')
            .execute()
        )

        rows_data = result_data.get('values', [])

        # Mapeia chaves compostas (Processo, Data) já existentes para evitar duplicidade
        chaves_existentes = set()
        for row in rows_data:
            p_val = ''
            d_val = ''
            if len(row) > idx_processo:
                p_val = row[idx_processo].strip()
            if len(row) > idx_data:
                d_val = row[idx_data].strip()

            # Normalização da data histórica do Sheets para bater exatamente com a do eproc
            if d_val:
                d_val = normalizar_data_br(d_val)

            if p_val and d_val:
                chaves_existentes.add((p_val, d_val))

        logger.info(f'Total de registros históricos lidos no Sheets: {len(chaves_existentes)}')

        # 3. Filtrar processos inéditos no lote atual
        novas_linhas = []
        processos_ineditos = []

        # Estrutura esperada de dados_processos: [{'processo': '...', 'data_inclusao': '...'}]
        for item in dados_processos:
            processo = item.get('processo', '').strip()
            data_inclusao = item.get('data_inclusao', '').strip()

            if not processo:
                continue

            # Normaliza a data do lote atual para o padrão brasileiro com hífen separador
            data_inclusao_normalizada = normalizar_data_br(data_inclusao)

            chave_composta = (processo, data_inclusao_normalizada)

            if chave_composta not in chaves_existentes:
                # Prepara os dados para gravação respeitando a posição exata mapeada
                tamanho_linha = max(idx_processo, idx_data) + 1
                linha = [''] * tamanho_linha
                linha[idx_processo] = processo
                # Salva usando o formato com hífen separador (não precisa de aspas simples pois o hífen impede a conversão automática do Sheets!)
                linha[idx_data] = data_inclusao_normalizada

                novas_linhas.append(linha)
                processos_ineditos.append(processo)

                # Registra no set local para evitar duplicatas dentro do mesmo lote novo
                chaves_existentes.add(chave_composta)

        # 4. Gravar em lote (append) apenas os registros inéditos
        if novas_linhas:
            logger.info(
                f'Gravando {len(novas_linhas)} novos processos inéditos no Google Sheets...'
            )
            body_append = {'values': novas_linhas}
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='A:Z',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body_append,
            ).execute()
            logger.success(
                f'Gravação realizada com sucesso! {len(novas_linhas)} linhas adicionadas.'
            )
        else:
            logger.info(
                'Todos os processos avaliados já haviam sido inseridos anteriormente. Nenhuma linha adicionada.'
            )

        return processos_ineditos

    except Exception as e:
        logger.error(f'Erro durante a gravação na planilha do Google Sheets: {e}')
        # Em caso de falha técnica severa na API do Google Sheets, retornamos lista vazia
        # para evitar enviar dados não gravados para o LegalMind (segurança transacional)
        return []
