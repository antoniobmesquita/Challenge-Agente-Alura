# 🤖 Agente de IA Corporativo - Base de Conhecimento Multidocumento

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/RAG-LangChain%20%2F%20LlamaIndex-green.svg)](#)
[![Status](https://img.shields.io/badge/Status-Concluído-green.svg)](#)

> **Challenge Alura + Oracle Next Education**: Um agente de Inteligência Artificial centralizado, seguro e acessível a todos os colaboradores para consultas rápidas e precisas em bases de conhecimento internas.

---

## 📌 Sobre o Projeto

Este projeto foi desenvolvido como parte do **Challenge Alura Agentes**. O objetivo principal é construir um **agente conversacional corporativo** utilizando técnicas de **RAG (Retrieval-Augmented Generation)**. 

O sistema permite que qualquer colaborador da empresa realize perguntas em linguagem natural e receba respostas contextualizadas, baseadas diretamente em documentos internos da organização (políticas de RH, diretrizes financeiras, processos operacionais, manuais técnicos, contratos, etc.), eliminando alucinações e citando as fontes de informação.

O projeto foi feito usando os documentos disponibilizados no challenge.
---

## 🎯 Principais Funcionalidades

- **🔍 Busca Semântica Avançada (RAG)**: Indexação vetorial para recuperar os trechos mais relevantes do documento antes de responder.
- **📌 Citação de Fontes**: Cada resposta gerada acompanha os metadados de origem (nome do arquivo, seção, página e data de atualização) para fácil auditabilidade.
- **🛡️ Prevenção de Alucinações & Fallback**: Caso a informação não seja encontrada nos documentos indexados, o agente informa explicitamente o limite do seu conhecimento e orienta o canal de contato adequado (ex: RH, TI, Financeiro).

---

## 🏗️ Arquitetura e Fluxo do RAG

```
[ Usuário / Colaborador ]
           │
           ▼
  ┌─────────────────┐
  │ Interface Chat  │ (Streamlit / Web)
  └────────┬────────┘
           │ (1. Pergunta)
           ▼
  ┌─────────────────┐       ┌──────────────────────┐
  │  Embedding &    │ ────> │  Banco de Dados      │
  │ Vector Search   │ <──── │  Vetorial            │
  └────────┬────────┘       └──────────────────────┘
           │ (2. Trechos/Contexto Recuperado)
           ▼
  ┌─────────────────┐       ┌──────────────────────┐
  │   Prompt RAG    │ ────> │ Modelo de Linguagem  │ (LLM)
  │  + Validação    │ <──── │    (Geração)         │
  └────────┬────────┘       └──────────────────────┘
           │ (3. Resposta Formatada + Fontes Citadas)
           ▼
[ Resposta Final ao Colaborador ]
```

### Etapas da Pipeline:
1. **Coleta e Organização de Documentos**: Coleta, limpeza e categorização dos arquivos internos por domínio.
2. **Processamento e Chunking**: Divisão dos textos em blocos otimizados com adição de metadados ricos.
3. **Indexação Vetorial**: Conversão de texto para vetores numéricos via embeddings e armazenamento em Vector DB.
4. **Geração e Validação**: Síntese da resposta restrita ao contexto recuperado e inclusão das referências bibliográficas.

---

## 🌐 Demonstração & Deploy

![Demonstração do Agente](sreenshots/print-agente.png)

![Demonstração do Agente](sreenshots/print-agente-2.png)

> **Link do Projeto Hospedado**: https://agente-mercado-central.streamlit.app/

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.10+
- **Framework de IA**: LangChain / LlamaIndex
- **Banco Vetorial / Indexação**: Pinecone
- **Interface de Usuário**: Streamlit
- **Processamento de Documentos**: PyPDF

---


## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
- Python 3.10 ou superior
- Git instalado
- Chaves de API configuradas (`.env`)

### Passos:

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. **Criar e ativar o ambiente virtual:**
   ```bash
   python -m venv venv
   # No Linux/macOS:
   source venv/bin/activate
   # No Windows:
   venv\Scripts\activate
   ```

3. **Instalar as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variáveis de ambiente:**
   Crie um arquivo `.env` na raiz do projeto com base no `.env.example`:
   ```env
   OCI_CONFIG_FILE=~/.oci/config
   OCI_PROFILE=DEFAULT
   OPENAI_API_KEY=sua_chave_aqui (se aplicável)
   ```

5. **Executar a aplicação:**
   ```bash
   streamlit run app.py
   ```

---

## 📄 Licença

Este projeto foi desenvolvido como parte do desafio da **Alura - Challenge Agentes de IA**. Sinta-se à vontade para 
