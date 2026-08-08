import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from google_tools import criar_entrevista_google_calendar, registrar_candidato

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(dotenv_path=str(PROJECT_ROOT / ".env"))

client = OpenAI(
    api_key=os.getenv("HUGGINGFACE_API_KEY"),
    base_url="https://router.huggingface.co/v1",
)

MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-20b")
PLANILHA_ID = os.getenv("PLANILHA_ID", "")


def build_agent_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "criar_entrevista_google_calendar",
                "description": "cria uma entrevista no Google Calendar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nome_candidato": {"type": "string", "description": "nome do candidato"},
                        "email_candidato": {"type": "string", "description": "email do candidato"},
                        "data_hora_inicio": {
                            "type": "string",
                            "description": "data e hora de início da entrevista (formato ISO 8601)",
                        },
                        "data_hora_fim": {
                            "type": "string",
                            "description": "data e hora de fim da entrevista (formato ISO 8601)",
                        },
                    },
                    "required": ["nome_candidato", "email_candidato", "data_hora_inicio", "data_hora_fim"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "registrar_candidato_planilha",
                "description": "salva os dados do usuário na planilha quando ele pedir para cadastrar, registrar ou salvar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string", "description": "Nome do candidato"},
                        "email": {"type": "string", "description": "Email do candidato"},
                        "vaga": {"type": "string", "description": "Nome da vaga. Se não informada, use 'Não informada'"},
                        "status": {"type": "string", "description": "Status da candidatura. Ex.: 'Agendado', 'Em análise'"},
                    },
                    "required": ["nome", "email", "vaga", "status"],
                },
            },
        },
    ]


def build_system_prompt():
    return (
        "Você é um agente de RH altamente especializado em recrutamento e seleção. "
        "Sua função é extrair informações de uma mensagem do usuário e "
        "chamar as ferramentas certas para agendar entrevistas e registrar candidatos."
    )


def executar_agente(mensagem_usuario, planilha_id=None):
    ferramentas = build_agent_tools()

    try:
        resposta = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": mensagem_usuario},
            ],
            tools=ferramentas,
            tool_choice="auto",
        )
        mensagem_assistente = resposta.choices[0].message
        resultados = []

        if getattr(mensagem_assistente, "tool_calls", None):
            for tool_call in mensagem_assistente.tool_calls:
                nome_funcao = tool_call.function.name
                argumentos = json.loads(tool_call.function.arguments)

                if nome_funcao == "criar_entrevista_google_calendar":
                    res = criar_entrevista_google_calendar(
                        argumentos["nome_candidato"],
                        argumentos["email_candidato"],
                        argumentos["data_hora_inicio"],
                        argumentos["data_hora_fim"],
                    )
                    resultados.append(("calendar", res))

                elif nome_funcao == "registrar_candidato_planilha":
                    res = registrar_candidato(
                        planilha_id or PLANILHA_ID,
                        argumentos["nome"],
                        argumentos["email"],
                        argumentos.get("vaga", "Não informada"),
                        argumentos.get("status", "Em análise"),
                    )
                    resultados.append(("sheets", res))

        if resultados:
            return resultados

        return [("texto", mensagem_assistente.content)]
    except Exception as e:
        return [("erro", str(e))]
