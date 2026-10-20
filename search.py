import os
import sys
from typing import List, Dict, Any
import chromadb
from app.services.embedding import LocalRobustEmbeddingFunction
from app.config import settings

def search(query: str, k: int = 4) -> List[Dict[str, Any]]:
    client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
    embed_fn = LocalRobustEmbeddingFunction(model_name=settings.EMBEDDING_MODEL, base_url=settings.OLLAMA_URL)
    try:
        col = client.get_collection("cisco_kb", embedding_function=embed_fn)
        results = col.query(query_texts=[query], n_results=k)
    except Exception as e:
        print(f"ChromaDB search note: {e}", file=sys.stderr)
        return []

    output = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metas = results.get("metadatas", [[]])[0]
        for doc, meta in zip(docs, metas):
            output.append({
                "source": meta.get("source"),
                "topic": meta.get("topic"),
                "chunk_index": meta.get("chunk_index"),
                "content": doc
            })
    return output

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "How do I configure OSPF area 0 and router-id?"
    print(f"Searching for: '{q}'\n")
    res = search(q, k=4)
    for i, r in enumerate(res, 1):
        print(f"[{i}] Source: {r['source']} | Topic: {r['topic']}")
        print(f"{r['content'][:250]}...\n" + "-"*50)
