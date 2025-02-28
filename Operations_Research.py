import streamlit as st
import os
import glob
from pinecone import Pinecone, ServerlessSpec
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA  # ✅ Importación correct0
from langchain_openai import OpenAIEmbeddings  # ✅ CORRECTO
from langchain_openai import ChatOpenAI  # ✅ CORRECTO
from langchain_pinecone import PineconeVectorStore  # ✅ CORRECTO


from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory  # ✅ CORRECTO
from langchain_community.tools import Tool
from langchain.agents import initialize_agent  # ✅ CORRECTO
from langchain.agents import AgentType  # ✅ CORRECTO
from langchain.memory import ConversationBufferMemory
from pinecone import Pinecone,ServerlessSpec
from dotenv import load_dotenv
import warnings



# Obtener API Key y entorno
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = "operations-research"



# Inicializar modelo de embeddings y LLM
embedding = OpenAIEmbeddings()
llm = ChatOpenAI(model_name="gpt-4.5-preview", temperature=0.1)

# 🔹 Cargar documentos solo una vez
@st.cache_resource
def load_documents(directory: str):
    """Carga y divide documentos PDF en fragmentos procesables."""
    documents = []
    pdf_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".pdf")]

    if not pdf_files:
        raise FileNotFoundError("❌ No se encontraron archivos PDF en el directorio.")

    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(docs)
        documents.extend(texts)

    return documents

# Ruta de documentos (¡Cambia esto a tu ruta real!)
DOCUMENTS_PATH = "C:/Users/gayar/Personal_Project/Documentos_Rag"
documents = load_documents(DOCUMENTS_PATH)

# 🔹 Inicializar Pinecone solo una vez
@st.cache_resource
def get_vectorstore():
    """Carga o crea el vectorstore en Pinecone."""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,
            metric="euclidean",
            spec=ServerlessSpec(
                cloud="aws",
                region="eu-east1"
            )
        )

    return PineconeVectorStore.from_existing_index(INDEX_NAME, embedding)

vectorstore = get_vectorstore()

# 🔹 Crear la cadena de búsqueda en documentos
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

# 🔹 Crear herramienta de búsqueda
retrieval_tool = Tool(
    name="Research Retriever",
    func=qa_chain.run,
    description="Busca información en la base de datos de investigación de operaciones."
)

# Verificar que la herramienta se haya creado correctamente
if retrieval_tool is None:
    raise ValueError("❌ La herramienta de búsqueda no se ha inicializado correctamente.")

# Lista de herramientas (debe contener al menos una)
tools = [retrieval_tool]
if not tools:
    raise ValueError("❌ No hay herramientas en la lista, el agente no podrá funcionar.")

# 🔹 Crear memoria del chatbot
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# 🔹 Inicializar el agente con herramientas
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    memory=memory
)



# 🔹 Interfaz en Streamlit
st.title("🤖 Hillier/Lieberman Corner")

user_input = st.text_input("✍️ What question do you have?")

if user_input:
    try:
        response = agent.invoke(user_input, handle_parsing_errors=True)
        output_text = response.get("output", "⚠️ No output generated.")

        # Mostrar la respuesta con formato Markdown
        st.markdown(f"### 📖 Answer:\n{output_text}", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"🚨 An error occurred: {e}")



