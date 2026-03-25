import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from loguru import logger

from src.config import settings

def get_drive_service():
    """Autentica e retorna o serviço do Google Drive usando Service Account."""
    if not settings.GOOGLE_APPLICATION_CREDENTIALS or not os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
        logger.warning(f"Credenciais do Google Drive não encontradas no caminho: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
        return None
        
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        creds = Credentials.from_service_account_file(
            settings.GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Erro ao autenticar no Google Drive: {e}")
        return None

def upload_to_drive(file_path: str, file_name: str = None, mime_type: str = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
    """Faz upload de um arquivo para o Google Drive."""
    if not settings.GOOGLE_DRIVE_FOLDER_ID:
        logger.warning("Falta GOOGLE_DRIVE_FOLDER_ID nas configurações. O upload para o Google Drive será ignorado.")
        return None
        
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado para upload: {file_path}")
        return None
        
    service = get_drive_service()
    if not service:
        return None
        
    try:
        if not file_name:
            file_name = os.path.basename(file_path)
        
        file_metadata = {
            'name': file_name,
            'parents': [settings.GOOGLE_DRIVE_FOLDER_ID]
        }
        
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        
        logger.info(f"Iniciando upload de {file_name} para o Google Drive...")
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True
        ).execute()
        
        file_id = file.get('id')
        logger.success(f"Upload concluído com sucesso. ID no Google Drive: {file_id}")
        return file_id
        
    except Exception as e:
        logger.error(f"Erro ao fazer upload para o Google Drive: {e}")
        return None

def search_file_in_drive(file_name: str) -> str:
    """Busca um arquivo pelo nome na pasta configurada do Google Drive e retorna seu ID, se existir."""
    if not settings.GOOGLE_DRIVE_FOLDER_ID:
        logger.warning("Falta GOOGLE_DRIVE_FOLDER_ID nas configurações.")
        return None

    service = get_drive_service()
    if not service:
        return None

    try:
        query = f"name='{file_name}' and '{settings.GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed=false"
        results = service.files().list(
            q=query, spaces='drive', fields='files(id, name)', supportsAllDrives=True, includeItemsFromAllDrives=True
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            return None
            
        logger.info(f"Arquivo '{file_name}' encontrado no Google Drive com ID: {items[0]['id']}")
        return items[0]['id']
        
    except Exception as e:
        logger.error(f"Erro ao buscar arquivo no Google Drive: {e}")
        return None

def download_from_drive(file_id: str, dest_path: str) -> bool:
    """Faz o download de um arquivo do Google Drive."""
    import io
    from googleapiclient.http import MediaIoBaseDownload
    
    service = get_drive_service()
    if not service:
        return False
        
    try:
        request = service.files().get_media(fileId=file_id)
        with open(dest_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                
        logger.success(f"Download do arquivo {file_id} concluído em {dest_path}.")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao fazer download do Google Drive: {e}")
        return False

def update_file_in_drive(file_id: str, file_path: str, mime_type: str = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
    """Atualiza um arquivo existente no Google Drive com um novo conteúdo local."""
    service = get_drive_service()
    if not service:
        return None
        
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado para upload: {file_path}")
        return None

    try:
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
        
        logger.info(f"Iniciando atualização do arquivo {file_id} no Google Drive...")
        
        file = service.files().update(
            fileId=file_id,
            media_body=media,
            fields='id',
            supportsAllDrives=True
        ).execute()
        
        logger.success(f"Atualização concluída com sucesso para o ID: {file.get('id')}")
        return file.get('id')
        
    except Exception as e:
        logger.error(f"Erro ao atualizar arquivo no Google Drive: {e}")
        return None

