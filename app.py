import uuid
import streamlit as st
from agente import responder


st.set_page_config(page_title="Agente Mercado Central")
st.title("Assistente de IA do Mercado Central")

if "messages" not in st.session_state:
   st.session_state.messages = []
if "thread_id" not in st.session_state:
   st.session_state.thread_id = str(uuid.uuid4())

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt:= st.chat_input("Digite sua mensagem"):
   st.session_state.messages.append({"role":"user", "content": prompt})
   with st.chat_message("user"):
      st.markdown(prompt)

   with st.spinner('Consultando os documentos...'):
      resposta = responder(prompt, thread_id=st.session_state.thread_id)

   st.session_state.messages.append({"role":"assistant", "content": resposta})

   with st.chat_message("assistant"):
         st.markdown(resposta)