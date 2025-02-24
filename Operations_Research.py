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


warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

# Obtener API Key y entorno
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

# Inicializar Pinecone correctamente
pc = Pinecone(api_key=PINECONE_API_KEY)



# Verificar que la API Key y el entorno están configurados
if not PINECONE_API_KEY:
    raise ValueError("La API Key de Pinecone no está configurada.")
###if not PINECONE_ENVIRONMENT:
###    raise ValueError("El entorno de Pinecone no está configurado.")

# Nombre del índice
index_name = "operations-research"

# Asegurar que `pc` está inicializado antes de llamarlo
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # Ajusta la dimensión según el modelo de embeddings
        metric='euclidean',
        spec=ServerlessSpec(
            cloud='aws',  # Usa 'gcp' en el plan gratuito
            region='us-east1'  # Región compatible con el plan gratuito
        )
    )

index = pc.Index(index_name)  # ✅ CORRECTO: Inicializar el índice correctamente
# Definir el modelo de embeddings
embedding = OpenAIEmbeddings()  # ✅ Ahora 'embedding' está definido

vectorstore = PineconeVectorStore.from_existing_index(index_name, embedding)  # ✅ CORRECTO






# Cargar documentos desde un directorio y procesarlos
def load_documents_from_directory(directory: str):
    documents = []
    pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
    for pdf_file in pdf_files:
        print(f"📖 Cargando documento: {os.path.basename(pdf_file)}") 
        loader = PyPDFLoader(pdf_file)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(docs)
        documents.extend(texts)
    print(f"✅ Total de fragmentos procesados: {len(documents)}")    
    return documents

# Crear e indexar la base de conocimiento en Pinecone
embedding = OpenAIEmbeddings()

retriever = vectorstore.as_retriever()

# Configurar modelo y QA Chain
llm = ChatOpenAI(model_name="gpt-4", temperature=0.1)
qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)

# Configurar memoria para chat
memory = ConversationBufferMemory(return_messages=True)


base_directory = "C:/Users/gayar/Personal_Project"
directory_path = os.path.join(base_directory, "Documentos_Rag")
documents = load_documents_from_directory(directory_path)



# Herramienta para resolver problemas matemáticos
def solve_math_problem(problem: str):
    try:
        from sympy import sympify
        return str(sympify(problem).evalf())
    except Exception as e:
        return f"Error al resolver el problema: {str(e)}"

math_tool = Tool(name="Math Solver", func=solve_math_problem, description="Resuelve problemas matemáticos básicos.")

# Crear agente con herramientas
agent = initialize_agent(
    tools=[math_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory
)


# Interfaz en Streamlit
st.title("OR Courseware")
user_input = st.text_input("What's your question:")

if user_input:
    if "resolver" in user_input.lower():
        response = agent.run(user_input)
    else:
        response = qa_chain.run(user_input)
    st.write(response)

