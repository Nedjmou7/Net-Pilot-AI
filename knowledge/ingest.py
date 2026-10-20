import os
import re
import math
import asyncio
import chromadb
from chromadb.config import Settings
import httpx
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_DIR = os.path.abspath(os.path.dirname(__file__))
CHROMA_PATH = os.path.abspath(os.getenv("CHROMA_PATH", os.path.join(KNOWLEDGE_DIR, "..", "chroma_data")))
COLLECTION_NAME = "cisco_kb"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", os.getenv("EMBED_MODEL", "nomic-embed-text"))


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split text into words roughly corresponding to tokens with overlap."""
    words = text.split()
    chunks = []
    step = chunk_size - overlap
    if step <= 0:
        step = chunk_size
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 30:
            chunks.append(chunk)
    return chunks


async def get_embedding(client: httpx.AsyncClient, text: str) -> list[float]:
    try:
        resp = await client.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=10.0
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("embedding", [])
    except Exception:
        pass
    # Deterministic pseudo-embedding fallback
    vec = [0.0] * 128
    words = text.lower().split()
    for i, w in enumerate(words[:128]):
        h = hash(w) % 128
        vec[h] += 1.0 / (1.0 + math.sqrt(i + 1))
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


async def is_ollama_online(client: httpx.AsyncClient) -> bool:
    try:
        resp = await client.get(f"{OLLAMA_URL}/api/tags", timeout=1.5)
        return resp.status_code == 200
    except Exception:
        return False


def compute_local_embedding(text: str) -> list[float]:
    vec = [0.0] * 128
    words = text.lower().split()
    for i, w in enumerate(words[:128]):
        h = hash(w) % 128
        vec[h] += 1.0 / (1.0 + math.sqrt(i + 1))
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


async def run_ingestion():
    os.makedirs(CHROMA_PATH, exist_ok=True)
    chroma = chromadb.PersistentClient(path=CHROMA_PATH, settings=Settings(anonymized_telemetry=False))
    # Reset or get collection
    try:
        chroma.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = chroma.create_collection(name=COLLECTION_NAME)

    docs_files = [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith(".md")]
    print(f"Ingesting {len(docs_files)} markdown files into ChromaDB '{COLLECTION_NAME}'...")

    total_chunks = 0
    async with httpx.AsyncClient() as client:
        ollama_active = await is_ollama_online(client)
        print(f"Ollama server status: {'Online' if ollama_active else 'Offline (Using local fast vectorizer)'}")

        all_ids = []
        all_embeddings = []
        all_documents = []
        all_metadatas = []

        for fname in docs_files:
            fpath = os.path.join(KNOWLEDGE_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            topic = title_match.group(1) if title_match else fname.replace(".md", "")

            chunks = chunk_text(content, chunk_size=250, overlap=40)
            for idx, ch in enumerate(chunks):
                if ollama_active:
                    emb = await get_embedding(client, ch)
                else:
                    emb = compute_local_embedding(ch)

                doc_id = f"{fname}_{idx}"
                all_ids.append(doc_id)
                all_embeddings.append(emb)
                all_documents.append(ch)
                all_metadatas.append({"source": fname, "topic": topic})
                total_chunks += 1

        # Batch insert into ChromaDB
        if all_ids:
            collection.add(
                ids=all_ids,
                embeddings=all_embeddings,
                documents=all_documents,
                metadatas=all_metadatas
            )

    print(f"Successfully indexed {total_chunks} chunks into ChromaDB at {CHROMA_PATH}!")


if __name__ == "__main__":
    asyncio.run(run_ingestion())
