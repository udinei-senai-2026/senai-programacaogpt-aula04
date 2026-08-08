# RecruAI

RecruAI é um agente de recrutamento em linguagem natural para auxiliar no agendamento de entrevistas e no registro de candidatos em planilhas. A aplicação usa inteligência artificial para interpretar mensagens do usuário e executar ações automáticas no Google Calendar e no Google Sheets.

## Descrição do agente

O agente recebe comandos em português, como por exemplo:

- agendar uma entrevista
- registrar um candidato em uma planilha
- criar um link de reunião no Google Meet

Ele interpreta a solicitação, extrai os dados necessários e realiza as operações correspondentes automaticamente.

## Principais funcionalidades

- Agendamento de entrevistas no Google Calendar
- Criação automática de reuniões com Google Meet
- Registro de candidatos em uma planilha do Google Sheets
- Interface simples em Streamlit para interação com o usuário
- Configuração centralizada via arquivo .env

## Serviços conectados

A aplicação integra os seguintes serviços:

- OpenAI / Hugging Face Router API para o modelo de linguagem do agente
- Google Calendar para criação de eventos e entrevistas
- Google Sheets para registrar candidatos na planilha
- Google OAuth para autenticação do usuário

## Estrutura do projeto

- main.py: ponto de entrada da aplicação
- ui.py: interface da aplicação em Streamlit
- agent.py: lógica do agente de IA e ferramentas
- google_tools.py: integração com Google Calendar e Google Sheets
- .env: variáveis de ambiente e configurações sensíveis

## Requisitos

- Python 3.10+
- Ambiente virtual Python
- Conta Google com acesso a Calendar e Sheets
- Chave de API do Hugging Face Router

## Como executar na máquina do usuário

1. Entre na pasta do projeto:

```bash
cd caminho/para/agente-people
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure o arquivo .env com as variáveis necessárias, por exemplo:

```env
HUGGINGFACE_API_KEY=sua_chave
PLANILHA_ID=seu_id_da_planilha
MODEL_NAME=openai/gpt-oss-20b
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
GOOGLE_TIMEZONE=America/Sao_Paulo
GOOGLE_CALENDAR_ID=primary
GOOGLE_SHEETS_RANGE=Página1!A:D
```

5. Certifique-se de que os arquivos de credenciais do Google estejam presentes:

- credentials.json
- token.json

6. Execute a aplicação:

```bash
streamlit run main.py
```

A aplicação ficará disponível no navegador em:

```text
http://localhost:8501
```

## Observações

- O arquivo .env não deve ser compartilhado publicamente.
- Para usar o Google Calendar e Google Sheets, o usuário precisa autorizar o acesso pela primeira vez.
- O fluxo de autenticação do Google cria o arquivo token.json automaticamente após a primeira execução.
