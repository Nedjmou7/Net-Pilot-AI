import os
import glob
from typing import List
import chromadb
from app.services.embedding import LocalRobustEmbeddingFunction
from app.config import settings

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
KNOWLEDGE_DIR = os.path.join(ROOT_DIR, "knowledge")
CHROMA_PATH = settings.CHROMA_PATH

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def ingest_knowledge():
    print(f"Connecting to ChromaDB at: {CHROMA_PATH}")
    os.makedirs(CHROMA_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection("cisco_kb")
    except Exception:
        pass

    embed_fn = LocalRobustEmbeddingFunction(model_name=settings.EMBEDDING_MODEL, base_url=settings.OLLAMA_URL)
    print(f"Embedding engine ready (Ollama online: {embed_fn.ollama_available}).")

    collection = client.create_collection(
        name="cisco_kb",
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"}
    )

    doc_files = sorted(glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md")))
    print(f"Found {len(doc_files)} markdown documents in {KNOWLEDGE_DIR}")

    total_chunks = 0
    ids = []
    documents = []
    metadatas = []

    for fpath in doc_files:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        first_line = content.split("\n")[0]
        topic = first_line.replace("#", "").strip() if first_line.startswith("#") else fname.replace(".md", "")

        chunks = chunk_text(content)
        for i, c in enumerate(chunks):
            chunk_id = f"{fname}_{i}"
            ids.append(chunk_id)
            documents.append(c)
            metadatas.append({"source": fname, "topic": topic, "chunk_index": i})
            total_chunks += 1

    batch_size = 50
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i+batch_size],
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )

    print(f"Successfully ingested {total_chunks} chunks from {len(doc_files)} documents into 'cisco_kb'!")

if __name__ == "__main__":
    ingest_knowledge()
