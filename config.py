# config.py
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    DOCUMENTS_DIR = "resumes"
    COLLECTION_NAME = "CVs"
    PERSISTENT_DIR = "data/chromadb"
    # Embedding
    MODEL_NAME = "text-embedding-3-small" #"all-mpnet-base-v2" per ollama
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    EMBEDDING_PROVIDER = "openai"  # Cambia in "openai" o "ollama" se necessario
    # Completamento
    ### ollama
    # LLM_MODEL = "llama3.2"  # "deepseek-r1:1.5b"  # "llama3.2" #  "deepseek-r1:1.5b"
    # AI_API_URL = "http://localhost:11434/v1"
    # AI_API_KEY = "ollama"
    ### openai
    MODEL_PATH = "modelli/mio_modello"
    OPENAI_EMBEDDINGS_KEY =os.getenv("OPENAI_API_KEY")
    LLM_MODEL = "gpt-4o-mini"
    LLM_MODEL_LOW = "gpt-4o-mini"
    AI_API_URL = "https://api.openai.com/v1/"
    AI_API_KEY = os.getenv("OPENAI_API_KEY")
