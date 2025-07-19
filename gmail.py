import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

# Permisos para leer y modificar Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


import datetime
from googleapiclient.discovery import build
import pandas as pd


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





def listar_correos_con_campos(service, days=7):
    hoy = datetime.datetime.now()
    inicio = (hoy - datetime.timedelta(days=days)).strftime('%Y/%m/%d')
    fin    = (hoy + datetime.timedelta(days=1)).strftime('%Y/%m/%d')
    query  = f'after:{inicio} before:{fin}'

    # 1) Listar IDs
    ids, req = [], service.users().messages().list(userId='me', q=query)
    while req:
        resp = req.execute()
        ids += [m['id'] for m in resp.get('messages', [])]
        req = service.users().messages().list_next(req, resp)

    # 2) Obtener labels map (ID → nombre)
    labels_resp = service.users().labels().list(userId='me').execute()
    labels_map  = {lbl['id']: lbl['name'] for lbl in labels_resp.get('labels', [])}

    datos = []
    for msg_id in ids:
        msg = service.users().messages().get(
            userId='me', id=msg_id, format='full'
        ).execute()
        hdrs = {h['name']: h['value'] for h in msg['payload']['headers']}

        # Mapear labelIds a nombres
        label_names = [labels_map.get(l, l) for l in msg.get('labelIds', [])]

        datos.append({
            'message_id':  msg_id,  # Agregar ID del mensaje
            'subject':     hdrs.get('Subject', ''),
            'from':        hdrs.get('From', ''),
            'to':          hdrs.get('To', ''),
            'date':        hdrs.get('Date', ''),
            'labels':      msg.get('labelIds', []),
            'label_names': label_names,
            'clasificacion': ""  # columna vacía para tu etiquetado manual
        })

    return datos

def _extraer_cuerpo(payload):
    """
    Busca en el payload la parte text/plain y devuelve su contenido.
    """
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                data = part['body'].get('data')
                if data:
                    import base64
                    return base64.urlsafe_b64decode(data).decode('utf-8')
    # fallback al snippet si no hay text/plain
    return payload.get('body', {}).get('data', '')


def mover_correo_a_spam(service, message_id):
    """
    Mueve un correo específico a la bandeja de spam
    """
    try:
        # Obtener los labels actuales del mensaje
        msg = service.users().messages().get(userId='me', id=message_id).execute()
        current_labels = msg.get('labelIds', [])
        
        # Preparar las modificaciones de labels
        labels_to_remove = []
        labels_to_add = ['SPAM']
        
        # Remover INBOX si está presente
        if 'INBOX' in current_labels:
            labels_to_remove.append('INBOX')
        
        # Aplicar los cambios
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={
                'addLabelIds': labels_to_add,
                'removeLabelIds': labels_to_remove
            }
        ).execute()
        
        return True
    except Exception as e:
        print(f"❌ Error moviendo correo {message_id} a spam: {e}")
        return False


def marcar_como_spam_batch(service, message_ids):
    """
    Mueve múltiples correos a spam de forma eficiente
    """
    if not message_ids:
        return 0
    
    exitosos = 0
    for msg_id in message_ids:
        if mover_correo_a_spam(service, msg_id):
            exitosos += 1
    
    return exitosos




def exportar_correos_a_excel(correos, filename="mis_correos_semana.xlsx"):
    # Crear DataFrame y quitar columnas innecesarias
    df = pd.DataFrame(correos)
    # Asegúrate de no tener body_text ni snippet
    for col in ['body_text', 'snippet']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
    # Exportar
    df.to_excel(filename, index=False)
    print(f"✅ {len(df)} correos exportados a '{filename}'")

if __name__ == '__main__':
    service = get_gmail_service()
    correos = listar_correos_con_campos(service, days=30)
    exportar_correos_a_excel(correos)



