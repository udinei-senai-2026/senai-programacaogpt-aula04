#dependências
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(dotenv_path=str(PROJECT_ROOT / ".env"))

#lista de permissões necessárias (scopes) para acessar a API do Google Drive
SCOPES = [ 
    #permissão para cria/editar eventos no Google Calendar
    'https://www.googleapis.com/auth/calendar',

    #permissão para ler/editar planilhas no Google Sheets
    'https://www.googleapis.com/auth/spreadsheets',
]

GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
GOOGLE_TIMEZONE = os.getenv("GOOGLE_TIMEZONE", "America/Sao_Paulo")
GOOGLE_SHEETS_RANGE = os.getenv("GOOGLE_SHEETS_RANGE", "Página1!A:D")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

#função para autenticar o usuário na conta do Google
def authenticar_google():

    #variável para armazenar as credenciais do usuário
    creds = None

    credentials_path = Path(GOOGLE_CREDENTIALS_FILE)
    token_path = Path(GOOGLE_TOKEN_FILE)

    if not credentials_path.is_absolute():
        credentials_path = PROJECT_ROOT / credentials_path
    if not token_path.is_absolute():
        token_path = PROJECT_ROOT / token_path

    #carrega o token salvo, se existir
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    #se não houver credenciais válidas, inicia o fluxo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            #token expirou, mas ainda pode ser renovado
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)

        #salva o token para reutilizar nas próximas execuções
        with open(token_path, 'w') as token:
            token.write(creds.to_json()) #escreve como formato JSON

    return creds #retorna as credenciais novas autenticada

#função para criar uma nova entrevista no google calendar
def criar_entrevista_google_calendar(
    nome_candidato,
    email_candidato,
    data_hora_inicio,
    data_hora_fim
):

    creds = authenticar_google() #obtem as credenciais do usuário
    service = build('calendar', 'v3', credentials=creds) #constrói o serviço da API do Google Calendar

    #dicionário cintendo as informações
    evento = {
        'summary': f'Entrevista de RH - {nome_candidato}', #título
        'description': f'Entrevista de agendamento com o time de People.', #descrição
        'start': {'dateTime': data_hora_inicio, 'timeZone': GOOGLE_TIMEZONE}, #data e hora de início
        'end': {'dateTime': data_hora_fim, 'timeZone': GOOGLE_TIMEZONE}, #data e hora de término
        'attendees': [{'email': email_candidato}], #lista de participantes
        'conferenceData':{#criar automaticamente a call
            'createRequest':{ #solicita a videoconferência
                'requestId': f"{uuid.uuid4()}", # gera id único
                'conferenceSolutionKey':{ #define que será no meet
                'type': 'hangoutsMeet'
                }
            }
        }
    }

    #envia o evento para o google calendar
    evento_criado = service.events().insert(
        
        calendarId=GOOGLE_CALENDAR_ID, #calendário configurado no ambiente
        body=evento, #corpo do evento
        conferenceDataVersion=1, #versão da conferência
        sendUpdates='all' #envia atualizações para todos os participantes
    ).execute() #executa a requisição

    link_meet = evento_criado.get('hangoutLink') #pega o link da call

    return f"sucesso! Entrevista criada com sucesso. Link da call: {link_meet}" #retorna mensagem de sucesso



#função responsável por registrar o candidato na planilha (Google Sheets)
def registrar_candidato(id_planilha, nome, email, vaga, status,):
    creds = authenticar_google() #obtem as credenciais do google
    service = build('sheets', 'v4', credentials=creds) #constrói o serviço da API do Google Sheets
    valores = [[nome, email, vaga, status]] #valores a serem inseridos na planilha
    spreadsheet_id = id_planilha or os.getenv("PLANILHA_ID", "")

    body = {
        'values': valores
            } #corpo da requisição

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, #id da planilha
        range=GOOGLE_SHEETS_RANGE, #intervalo de células a serem preenchidas
        valueInputOption='USER_ENTERED', #opção de entrada de valores
        body=body #corpo da requisição
    ).execute() #executa a requisição

    return f"sucesso! {nome} foi registrado(a) com status" #retorna mensagem de sucesso
