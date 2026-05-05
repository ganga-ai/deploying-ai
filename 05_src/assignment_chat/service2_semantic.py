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

def ask_ttc_question(question: str) -> str:
    try:
        # 1. Embed the query
        embedding = client_openai.embeddings.create(
            model="text-embedding-3-small",
            input=[question]
        ).data[0].embedding

        # 2. Retrieve top chunks
        results = collection.query(
            query_embeddings=[embedding],
            n_results=3
        )

        docs = results.get("documents", [[]])[0]

        if not docs:
            return "I don't know based on the available data."

        # 3. Build context
        context = "\n\n".join(docs)

        # 4. Ask LLM
        prompt = f"""
        Answer the question using ONLY the context below.
        If the answer is not present, say you don't know.

        Context:
        {context}

        Question:
        {question}
        """

        response = client_openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {e}"