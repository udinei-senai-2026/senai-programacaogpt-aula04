import os
from pathlib import Path

import streamlit as st

from agent import executar_agente

PROJECT_ROOT = Path(__file__).resolve().parent


def configurar_interface():
    st.set_page_config(page_title="RecruAI", page_icon="🤖", layout="wide")

    with st.sidebar:
        st.title("Painel do Sistema")
        st.markdown("---")

        st.subheader("Status do ambiente")
        if os.getenv("HUGGINGFACE_API_KEY"):
            st.success("Hugging Face API: Conectada")
        else:
            st.error("Hugging Face API: Chave não encontrada")

        credentials_path = os.path.join(PROJECT_ROOT, os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json"))
        if os.path.exists(credentials_path):
            st.success("Google Credentials: OK")
        else:
            st.error("Google Credentials: Ausente")

        st.markdown("---")
        st.info("Modelo em uso: **`openai/gpt-oss-20b` via Hugging Face Router API")

        if "prompt_input" not in st.session_state:
            st.session_state["prompt_input"] = ""


def aplicar_sugestao(texto):
    st.session_state.prompt_input = texto


def renderizar_interface():
    configurar_interface()

    st.markdown("### Sugestões rápidas:")

    col1, col2, col3 = st.columns(3)

    with col1:
        sugestao1 = "Marque uma entrevista com a pessoa com <nome-pessoa> (<email-pessoa>) para <dia> das <hora-inicio> às <hora-fim>. Para a vaga <nome-vaga> e registre na planilha com o status 'Agendado')"
        if st.button("Agendar reunião + Planilha", use_container_width=True):
            aplicar_sugestao(sugestao1)

    with col2:
        sugestao2 = "Registre <nome-pessoa> (<email-pessoa>) na planilha para a vaga <nome-vaga> com o status <status>"
        if st.button("Apenas cadastrar na planilha", use_container_width=True):
            aplicar_sugestao(sugestao2)

    with col3:
        sugestao3 = "Agende uma conversa rápida de 30 minutos com <nome-pessoa> (<email-pessoa>) para amanhã às <hora-inicio>."
        if st.button("Criar Link Meet", use_container_width=True):
            aplicar_sugestao(sugestao3)

    st.markdown("<br>", unsafe_allow_html=True)

    prompt_usuario = st.text_area(
        "Digite sua instrução para o agente: ",
        value=st.session_state.prompt_input,
        placeholder="Ex.: Agende uma entrevista para o candidato...",
    )

    if st.button("Processar solicitação", type="primary", use_container_width=True):
        if not prompt_usuario.strip():
            st.warning("Por favor, digite ou selecione um comando.")
        else:
            with st.spinner("Processando informações..."):
                retorno = executar_agente(prompt_usuario, planilha_id=os.getenv("PLANILHA_ID", ""))
                st.markdown("---")
            st.markdown("Resultados da processamento")

            for tipo, resultado in retorno:
                if tipo == "calendar":
                    st.success(f"Google Agenda: {resultado}")
                elif tipo == "sheets":
                    st.success(f"Google Sheets: {resultado}")
                elif tipo == "texto":
                    st.info(f"Mensagem do agente: {resultado}")
                elif tipo == "erro":
                    st.error(f"Erro: {resultado}")
