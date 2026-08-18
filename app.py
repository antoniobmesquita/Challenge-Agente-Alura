import uuid
import streamlit as st
from agente import responder


st.set_page_config(page_title="Agente Mercado Central", page_icon="🛒")
st.title("Assistente de IA do Mercado Central")

st.markdown("##### Assistente feito para responder suas dúvidas sobre atendimento, regulamento ou politicas internas.")

if "messages" not in st.session_state:
   st.session_state.messages = []
if "thread_id" not in st.session_state:
   st.session_state.thread_id = str(uuid.uuid4())

with st.sidebar:
    if st.button(" Nova conversa"):
      st.session_state.messages = []
      st.session_state.thread_id = str(uuid.uuid4())
      st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt:= st.chat_input("Digite sua mensagem"):
   st.session_state.messages.append({"role":"user", "content": prompt})
   with st.chat_message("user"):
      st.markdown(prompt)

   with st.spinner('Consultando os documentos...'):
      try:
         resposta = responder(prompt, thread_id=st.session_state.thread_id)
      except Exception as e:
          erro_str = str(e).lower()
          if "token" in erro_str or "context_length" in erro_str or "maximum context" in erro_str:
            resposta = (
               "⚠️ A conversa ficou muito longa e ultrapassou o limite de tokens do modelo. "
               "Por favor, inicie uma nova conversa (recarregue a página) ou envie uma pergunta mais curta."
            )
            st.error(resposta)
          else:
            resposta = "❌ Ocorreu um erro ao consultar o assistente. Tente novamente em instantes."
            st.error(f"Erro inesperado: {e}")

   st.session_state.messages.append({"role":"assistant", "content": resposta})

   with st.chat_message("assistant"):
         st.markdown(resposta)