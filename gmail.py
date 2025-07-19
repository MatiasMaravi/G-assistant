import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Solo lectura de Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


import datetime
from googleapiclient.discovery import build

def listar_correos_semana(service):
    # Fecha de hoy y hace 7 días
    hoy = datetime.datetime.now()
    hace_7_dias = hoy - datetime.timedelta(days=7)

    # Gmail espera fechas en formato YYYY/MM/DD
    fecha_inicio = hace_7_dias.strftime('%Y/%m/%d')
    # Opcional: limitar hasta mañana para excluir correos de hoy después de la hora actual
    mañana = (hoy + datetime.timedelta(days=1)).strftime('%Y/%m/%d')

    # Construye la query: correos desde hace 7 días hasta hoy
    query = f'after:{fecha_inicio} before:{mañana}'

    mensajes = []
    request = service.users().messages().list(userId='me', q=query)
    while request is not None:
        resp = request.execute()
        mensajes.extend(resp.get('messages', []))
        request = service.users().messages().list_next(request, resp)

    print(f"Encontrados {len(mensajes)} correos en los últimos 7 días:\n")
    for m in mensajes:
        msg = service.users().messages().get(
            userId='me',
            id=m['id'],
            format='metadata',
            metadataHeaders=['Date','From','Subject']
        ).execute()
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        print(f"- {headers.get('Date')} | {headers.get('From')} | {headers.get('Subject')}")



def get_gmail_service():
    creds = None
    # Token de acceso guardado tras primer login
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Si no existe o expiró, forzamos nuevo OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Guardamos para próximos runs
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

if __name__ == '__main__':
    service = get_gmail_service()
    listar_correos_semana(service)

