import os
from src.utils.google_sheets import get_sheets_service, normalizar_data_br
from src.config import settings


def main():
    service = get_sheets_service()
    if not service:
        print('Serviço indisponível')
        return

    spreadsheet_id = '1ZoB5WItw1KwY4zIkrfLhAtWmgIDMbLNJRaCSM0Il6po'

    # Teste de Gravação com Hífen Separador
    teste_linha = ['18/05/2026 - 14:30:15', '0002729-11.2019.8.27.2716-TESTE-SEPARADOR']
    print(f"\nSimulando gravação com hífen separador: {teste_linha}")
    
    body_append = {'values': [teste_linha]}
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range='A:B',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body_append,
    ).execute()

    
    # 2. Ler linhas de dados usando o padrão FORMATTED_VALUE
    result_data = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range='A2:Z100')
        .execute()
    )
    rows = result_data.get('values', [])
    print('\nLinhas brutas do Sheets (Padrão FORMATTED_VALUE após gravação RAW):')
    for i, r in enumerate(rows):
        if len(r) > 1 and 'TESTE-RAW' in str(r[1]):
            print(f'Linha {i+2} (TESTE): {r}')
        elif i < 10:  # Limita a exibição do histórico
            print(f'Linha {i+2}: {r}')

if __name__ == '__main__':
    main()

