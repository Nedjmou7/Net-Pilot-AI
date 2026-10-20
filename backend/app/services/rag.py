import os
import re
import logging
from typing import List, Dict, Any, Tuple
import httpx
from app.config import settings
from app.services.ollama_client import ollama_client

logger = logging.getLogger("topogemma.rag")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
KNOWLEDGE_DIR = os.path.join(ROOT_DIR, "knowledge")

# Fallback lightweight keyword/semantic indexer across markdown files
def search_local_files(query: str, k: int = 4) -> List[Dict[str, Any]]:
    results = []
    if not os.path.exists(KNOWLEDGE_DIR):
        return results

    q_words = set(re.findall(r"\w+", query.lower()))
    if not q_words:
        return results

    scored_docs = []
    for fname in os.listdir(KNOWLEDGE_DIR):
        if fname.endswith(".md"):
            fpath = os.path.join(KNOWLEDGE_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                # Compute word match score
                content_lower = content.lower()
                score = sum(1 for w in q_words if w in content_lower)
                # Boost title matches
                title = fname.replace(".md", "").replace("-", " ")
                score += sum(3 for w in q_words if w in title.lower())

                if score > 0:
                    scored_docs.append((score, fname, content))
            except Exception:
                continue

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    for score, fname, content in scored_docs[:k]:
        results.append({
            "source": fname,
            "topic": fname.replace(".md", "").replace("-", " ").title(),
            "content": content[:1200]
        })
    return results

def query_chromadb(query: str, k: int = 4) -> List[Dict[str, Any]]:
    """Query ChromaDB collection 'cisco_kb' if available."""
    try:
        import chromadb
        from app.services.embedding import LocalRobustEmbeddingFunction
        client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        collections = client.list_collections()
        has_kb = any(c.name == "cisco_kb" for c in collections)
        if not has_kb:
            return search_local_files(query, k)

        embed_fn = LocalRobustEmbeddingFunction(model_name=settings.EMBEDDING_MODEL, base_url=settings.OLLAMA_URL)
        col = client.get_collection(name="cisco_kb", embedding_function=embed_fn)
        results = col.query(query_texts=[query], n_results=k)

        out = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results.get("metadatas", [[]])[0]
            for doc, meta in zip(docs, metas):
                out.append({
                    "source": meta.get("source", "cisco_kb.md"),
                    "topic": meta.get("topic", "Networking"),
                    "content": doc
                })
        return out if out else search_local_files(query, k)
    except Exception as e:
        logger.debug(f"ChromaDB query fallback: {e}")
        return search_local_files(query, k)

async def answer_with_rag(user_message: str, intent: str = "question") -> Tuple[str, List[str]]:
    chunks = query_chromadb(user_message, k=4)
    sources = list(dict.fromkeys([c["source"] for c in chunks]))

    if not chunks:
        # Generic helpful answer
        return (
            "I could not locate specific reference docs in the local Cisco knowledge base for this query. "
            "Please check that knowledge documents are ingested into ChromaDB.",
            []
        )

    context_str = "\n\n---\n\n".join(
        f"Source: {c['source']} ({c['topic']})\n{c['content']}" for c in chunks
    )

    if intent == "troubleshoot":
        sys_prompt = (
            "You are TopoGemma, an expert Cisco network troubleshooting engineer. "
            "Analyze the problem using the provided reference documentation and troubleshooting steps.\n"
            "Systematic Checklist:\n"
            "1. Verify IP address, subnet mask, and default gateway settings.\n"
            "2. Verify physical interface state (up/up) and cable type (straight vs crossover).\n"
            "3. Check VLAN membership, trunk port configuration, and allowed VLANs.\n"
            "4. Verify routing table entries, OSPF neighbors, and router subinterface dot1Q encapsulation.\n"
            "5. Inspect Access Control Lists (ACLs) for dropped packets.\n\n"
            "Answer ONLY using facts from the provided context. If the answer is not in the context, say 'I am not sure based on the local knowledge base.' "
            "Cite the source document names (e.g. [source-name.md]) in your response."
        )
    else:
        sys_prompt = (
            "You are TopoGemma, a Cisco certified networking instructor. "
            "Answer the student's question accurately and concisely.\n"
            "Answer ONLY using the provided knowledge base context below. "
            "If the answer cannot be determined from the context, say 'I am not sure based on the local documentation.' "
            "Cite the source document name(s) at the end of your answer."
        )

    user_prompt = f"Knowledge Context:\n{context_str}\n\nStudent Request:\n{user_message}"

    try:
        res = await ollama_client.chat(
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            format_json=False,
            temperature=0.2
        )
        reply = res.get("message", {}).get("content", "").strip()
        if reply:
            return reply, sources
    except Exception as e:
        logger.info(f"Ollama offline during RAG generation ({e}), formatting synthesized response from knowledge base.")

    # High-quality deterministic fallback response built directly from retrieved chunks
    top_chunk = chunks[0]
    fallback_reply = (
        f"### {top_chunk['topic']} Analysis\n\n"
        f"{top_chunk['content']}\n\n"
        f"**Sources Consulted**: {', '.join(sources)}"
    )
    return fallback_reply, sources
