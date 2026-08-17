import os
from dotenv import load_dotenv
 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()
pinecone_key= os.getenv("PINECONE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
os.getenv("HF_TOKEN")

embed_model = HuggingFaceEmbeddings(model_name="ricardo-filho/bert-base-portuguese-cased-nli-assin-2")

vectorstore = PineconeVectorStore(
    host = "https://projeto-agente-tam67bn.svc.aped-4627-b74a.pinecone.io",
    pinecone_api_key = pinecone_key,
    embedding = embed_model
)

def formatar_contexto(documentos):
  """
  Recebe a lista de Document retornada pelo retriever e monta um bloco
  de texto limpo para o LLM, incluindo metadados de origem para permitir
  a citação de fonte na resposta (card 5 do Trello).
  """

  blocos = []
  for doc in documentos:
    origem = doc.metadata.get('source', 'documento desconhecido')
    nome_arquivo = origem.split('/')[-1]
    secao = doc.metadata.get('secao', 'seção desconhecida')
    pagina = doc.metadata.get('page_label', '?')
    bloco = f"Fonte: {nome_arquivo}, seção: {secao}, página: {pagina}\n\n{doc.page_content}"
    blocos.append(bloco)
  return "\n\n".join(blocos)


@tool

def ferramenta_manual(pergunta: str) -> str:
  """Utilize essa ferramenta sempre que o usuário fizer
  uma pergunta sobre o manual de fornecedores e políticas de compras.
  """
  retriever_manual = vectorstore.as_retriever(search_kwargs={"k":10,"namespace":"manual-fornecedores-politicas-compras"})
  documentos = retriever_manual.invoke(pergunta)
  return formatar_contexto(documentos)

@tool

def ferramenta_faq(pergunta: str) -> str:
  """Utilize essa ferramenta sempre a resposta
  do usuário estiver em perguntas frequentes.
  """
  retriever_faq = vectorstore.as_retriever(search_kwargs={"k":10,"namespace":"perguntas-frequentes"})

  documentos = retriever_faq.invoke(pergunta)
  return formatar_contexto(documentos)

@tool

def ferramenta_regulamento(pergunta: str) -> str:
    """Utilize essa ferramenta sempre que o suário
    fizer uma pergunta relacionada ao regulamento interno.
    """
    retriever_regulamento = vectorstore.as_retriever(search_kwargs={"k":10,"namespace":"regulamento-interno-e-procedimentos"})

    documentos = retriever_regulamento.invoke(pergunta)

    return formatar_contexto(documentos)

@tool
def ferramenta_atendimento(pergunta: str) -> str:
  """Utilize essa ferramenta sempre que o usuário
    fizer uma pergunta relacionada à política de atendimento, trocas e devoluções.
  """

  retriever_atendimento = vectorstore.as_retriever(search_kwargs={"k":10, "namespace":"politica-atendimento-trocas-devolucoes"})
  documentos = retriever_atendimento.invoke(pergunta)
  return formatar_contexto(documentos)

tools = [ferramenta_manual, ferramenta_faq, ferramenta_regulamento, ferramenta_atendimento]

modelo = ChatGroq(
    groq_api_key = groq_api_key,
    model_name = "openai/gpt-oss-120b"
)

prompt_sistema= """
  Você é um assistente virtual do Mercado Central 24h, especializado em responder
  perguntas de colaboradores e clientes com base nos documentos internos da empresa.
  
  Se apresente como o agente do Mercado Central.

  Seja sempre solicito e atencioso

  Ao receber uma pergunta, use a ferramenta mais adequada para buscar informações
  relevantes antes de responder. Você pode usar mais de uma ferramenta se a pergunta
  exigir informações de mais de um documento.
  
  Responda EXCLUSIVAMENTE com base no conteúdo retornado pelas ferramentas. Nunca
  use conhecimento próprio ou invente informações que não estejam no contexto.
  
  Sempre cite a fonte da informação ao final da resposta, no formato
  "(Fonte: nome do documento, Seção X, Página Y)", usando os dados de
  [Fonte: ...] presentes no contexto retornado pelas ferramentas.
  
  Se a informação não estiver disponível em nenhum dos documentos consultados,
  diga claramente que não encontrou essa informação e, quando fizer sentido,
  sugira o canal de contato adequado (SAC, RH, Ouvidoria) com base no que os
  documentos indicarem.
  """
agente_mercado = create_agent(
      model=modelo,
      tools=tools,
      system_prompt=prompt_sistema,
      checkpointer=InMemorySaver()
  )

def responder(pergunta:str, thread_id:str) -> str:
  """
    Recebe a pergunta do usuário em texto puro e devolve a resposta final
    do agente, já pronta para ser exibida na interface.
  """
  resultado = agente_mercado.invoke({"messages": [{"role": "user", "content": pergunta}]},
        config={"configurable": {"thread_id": thread_id},"recursion_limit": 10})

  return resultado["messages"][-1].content