import os
from openai import OpenAI
from dotenv import load_dotenv

# Loading API key from secret.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, "../.secrets")
load_dotenv(dotenv_path, override=True)
API_KEY = os.getenv("API_GATEWAY_KEY")

# Creating an OpenAI client.
client_openai = OpenAI(
    base_url = "https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
    api_key = os.getenv("API_GATEWAY_KEY"),
    default_headers = {"x-api-key": os.getenv("API_GATEWAY_KEY")}
)

import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="ttc_docs")

DOCS_PATH = os.path.join(BASE_DIR, "../documents/ttc_docs")

# --- Helper: infer topic from filename ---
def get_topic(filename):
    if filename.startswith("line"):
        return "subway_line"
    elif filename.startswith("route"):
        return "route_info"
    elif "presto" in filename:
        return "presto"
    elif "fare" in filename:
        return "fare_rules"
    elif "policy" in filename:
        return "policy"
    elif "faq" in filename:
        return "faq"
    else:
        return "general"
    
# --- Helper: chunk text ---
def chunk_text(text, chunk_size=400, overlap=80):
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap

    return chunks


# --- Main ---
all_docs = []
all_meta = []
all_ids = []
    
for filename in os.listdir(DOCS_PATH):
    if not filename.endswith(".txt"):
        continue
    
    filepath = os.path.join(DOCS_PATH, filename)
    
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
        
    chunks = chunk_text(text)
    topic = get_topic(filename)
    
    for idx, chunk in enumerate(chunks):
        all_docs.append(chunk)
        all_meta.append({
            "source": filename,
            "topic": topic,
            "chunk_id": idx
        })
        all_ids.append(f"{filename}_{idx}")
        
# --- Create embeddings ---
embeddings = client_openai.embeddings.create(
    model="text-embedding-3-small",
    input=all_docs
).data

embedding_vectors = [e.embedding for e in embeddings]

# --- Store in ChromaDB ---
collection.add(
    documents=all_docs,
    metadatas=all_meta,
    ids=all_ids,
    embeddings=embedding_vectors
)

print("Embeddings stored successfully.")
