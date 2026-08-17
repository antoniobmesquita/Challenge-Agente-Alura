from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
import re
import os
from dotenv import load_dotenv

load_dotenv()

pinecone_key= os.getenv("PINECONE_API_KEY")
os.getenv("HF_TOKEN")

manual_fornecedores = "documentos/Manual de Fornecedores e Política de Compras — Mercado Central 24h (PT-BR).pdf"
perguntas_frequentes = "documentos/Perguntas Frequentes (FAQ) — Clientes e Funcionários — Mercado Central 24h (PT-BR).pdf"
regulamento_interno = "documentos/Regulamento Interno e Procedimentos Operacionais — Mercado Central 24h (PT-BR).pdf"
politica_atendimento = "documentos/Política de Atendimento, Trocas e Devoluções — Mercado Central 24h (PT-BR).pdf"



loader_manual = PyPDFLoader(manual_fornecedores).load()
loader_faq = PyPDFLoader(perguntas_frequentes).load()
loader_regulamento = PyPDFLoader(regulamento_interno).load()
loader_atendimento = PyPDFLoader(politica_atendimento).load()

def limpar_texto(texto):
    """
    Aplica a sequência de limpeza definida para os PDFs do projeto.
    Recebe o page_content de um Document e devolve o texto limpo.
    """
    texto = re.sub(r'```(?:text)?\n?', '', texto)
    texto = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', texto)
    texto = re.sub(r'(?m)^#{1,6}\s+', '', texto)
    texto = re.sub(r'(?m)^>\s?', '', texto)
    texto = re.sub(r'\[\s?\]\s*', '', texto)
    texto = re.sub(r'`([^`]+)`', r'\1', texto)
    texto = re.sub(r'\n?-{3,}\n?', '\n', texto)
    texto = re.sub(r'([a-zà-ú\)\?\.:])([A-ZÀ-Ú])', r'\1 \2', texto)
    texto = re.sub(r'[ \t]+', ' ', texto)
    texto = re.sub(r' *\n *', '\n', texto)
    texto = re.sub(r'\n{3,}', '\n\n', texto)

    return texto.strip()

for doc in loader_manual:
    doc.page_content = limpar_texto(doc.page_content)

for doc in loader_faq:
    doc.page_content = limpar_texto(doc.page_content)

for doc in loader_regulamento:
    doc.page_content = limpar_texto(doc.page_content)

for doc in loader_atendimento:
    doc.page_content = limpar_texto(doc.page_content)

def extrair_metadados_fixos(documentos, categoria):
    texto_primeira_pagina = documentos[0].page_content

    match_departamento = re.search(
        r'Departamento(?:\s+Respons[aá]vel)?:\s*(.+)',
        texto_primeira_pagina
    )
    departamento = match_departamento.group(1).strip() if match_departamento else ""

    match_data_emissao = re.search(
        r'Data de (?:Emiss[aã]o|Atualiza[cç][aã]o|Vig[eê]ncia):\s*(.+)',
        texto_primeira_pagina
    )
    data_documento = match_data_emissao.group(1).strip() if match_data_emissao else ""

    match_revisao = re.search(
        r'[UÚ]ltima Revis[aã]o:\s*(.+)',
        texto_primeira_pagina
    )
    ultima_revisao = match_revisao.group(1).strip() if match_revisao else ""

    for doc in documentos:
        doc.metadata['categoria'] = categoria
        doc.metadata['departamento_responsavel'] = departamento
        doc.metadata['data_documento'] = data_documento
        doc.metadata['ultima_revisao'] = ultima_revisao

    return documentos

loader_manual = extrair_metadados_fixos(loader_manual, categoria="Manual de Fornecedores e Política de Compras")
loader_faq = extrair_metadados_fixos(loader_faq, categoria="Perguntas Frequentes")
loader_regulamento = extrair_metadados_fixos(loader_regulamento, categoria="Regulamento Interno e Procedimentos Operacionais")
loader_atendimento = extrair_metadados_fixos(loader_atendimento, categoria="Política de Atendimento, Trocas e Devoluções")

tokenizer = AutoTokenizer.from_pretrained("ricardo-filho/bert-base-portuguese-cased-nli-assin-2")
splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    tokenizer = tokenizer,
    chunk_size= 512,
    chunk_overlap = 50
)
pedacos_manual = splitter.split_documents(loader_manual)
pedacos_faq = splitter.split_documents(loader_faq)
pedacos_regulamento = splitter.split_documents(loader_regulamento)
pedacos_atendimento = splitter.split_documents(loader_atendimento)

def atribuir_secoes(chunks):
    padrao_secao = re.compile(r'^\d+(?:\.\d+)?\.?\s+[A-ZÀ-Ú].+', re.MULTILINE)
    secao_atual = ""

    for chunk in chunks:
        titulos_encontrados = padrao_secao.findall(chunk.page_content)
        if titulos_encontrados:
            secao_atual = titulos_encontrados[-1].strip()
        chunk.metadata['secao'] = secao_atual

    return chunks
pedacos_manual = atribuir_secoes(pedacos_manual)
pedacos_faq = atribuir_secoes(pedacos_faq)
pedacos_regulamento = atribuir_secoes(pedacos_regulamento)
pedacos_atendimento = atribuir_secoes(pedacos_atendimento)

embed_model = HuggingFaceEmbeddings(model_name="ricardo-filho/bert-base-portuguese-cased-nli-assin-2")

vectorstore = PineconeVectorStore(
    host = "https://projeto-agente-tam67bn.svc.aped-4627-b74a.pinecone.io",
    pinecone_api_key = pinecone_key,
    embedding = embed_model
)

vectorstore.delete(delete_all=True,namespace="manual-fornecedores-politicas-compras")
vectorstore.add_documents(
    pedacos_manual,
    ids = [str(i) for i in range(len(pedacos_manual))],
    namespace="manual-fornecedores-politicas-compras"
)

vectorstore.delete(delete_all=True,namespace="perguntas-frequentes")
vectorstore.add_documents(
    pedacos_faq,
    ids = [str(i) for i in range(len(pedacos_faq))],
    namespace="perguntas-frequentes"
)

vectorstore.delete(delete_all=True,namespace="regulamento-interno-e-procedimentos")
vectorstore.add_documents(
    pedacos_regulamento,
    ids = [str(i) for i in range(len(pedacos_regulamento))],
    namespace="regulamento-interno-e-procedimentos"
)

vectorstore.delete(delete_all=True, namespace="politica-atendimento-trocas-devolucoes")
vectorstore.add_documents(
    pedacos_atendimento,
    ids = [str(i) for i in range(len(pedacos_atendimento))],
    namespace="politica-atendimento-trocas-devolucoes"
)

resultado = vectorstore.similarity_search(
    "quais são os canais de atendimento",
    namespace="politica-atendimento-trocas-devolucoes",
    k=2
)
for r in resultado:
    print(r.metadata.get('secao'), '-', r.page_content[:80])