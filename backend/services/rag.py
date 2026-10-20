import os
import re
import math
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings
import httpx
from dotenv import load_dotenv
from backend.services import ollama_client

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")))
COLLECTION_NAME = "cisco_kb"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", os.getenv("EMBED_MODEL", "nomic-embed-text"))

_chroma_client = None
_collection = None


def get_chroma_collection():
    global _chroma_client, _collection
    if _collection is None:
        os.makedirs(CHROMA_PATH, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH, settings=Settings(anonymized_telemetry=False))
        _collection = _chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


_ollama_checked = False
_ollama_available = False
NETWORK_TERMS = {
    "cisco", "router", "switch", "vlan", "ospf", "rip", "eigrp", "bgp",
    "subnet", "ip address", "gateway", "dhcp", "dns", "nat", "acl",
    "firewall", "etherchannel", "stp", "trunk", "packet tracer", "ios",
    "ping", "tcp", "udp", "ethernet", "network", "routing", "interface"
}


def is_network_question(query: str) -> bool:
    lower_query = query.lower()
    return any(term in lower_query for term in NETWORK_TERMS)


async def check_ollama_available() -> bool:
    global _ollama_checked, _ollama_available
    if not _ollama_checked:
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                resp = await client.get(f"{OLLAMA_URL}/api/tags")
                _ollama_available = resp.status_code == 200
        except Exception:
            _ollama_available = False
        _ollama_checked = True
    return _ollama_available


async def get_embedding(text: str) -> List[float]:
    """Query Ollama embedding endpoint with fallback."""
    if await check_ollama_available():
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.post(
                    f"{OLLAMA_URL}/api/embeddings",
                    json={"model": EMBED_MODEL, "prompt": text}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("embedding", [])
        except Exception:
            pass
    # Deterministic pseudo-embedding for local fallback (128-dim vector)
    vec = [0.0] * 128
    words = text.lower().split()
    for i, w in enumerate(words[:128]):
        h = hash(w) % 128
        vec[h] += 1.0 / (1.0 + math.sqrt(i + 1))
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def fallback_text_search(query: str, k: int = 4) -> List[Dict[str, Any]]:
    """Local text matching fallback if vector collection is empty."""
    knowledge_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge"))
    if not os.path.exists(knowledge_dir):
        return []

    tokens = set(re.findall(r'\w+', query.lower()))
    scored_docs: List[Tuple[float, str, str, str]] = []

    for fname in os.listdir(knowledge_dir):
        if fname.endswith(".md"):
            fpath = os.path.join(knowledge_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                words = set(re.findall(r'\w+', content.lower()))
                common = tokens.intersection(words)
                score = len(common)
                if score > 0:
                    scored_docs.append((score, content[:600], fname, fname.replace(".md", "")))
            except Exception:
                pass

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, content, source, topic in scored_docs[:k]:
        results.append({
            "content": content,
            "source": source,
            "topic": topic
        })
    return results


async def search_knowledge(query: str, k: int = 4) -> List[Dict[str, Any]]:
    """Query ChromaDB for relevant Cisco knowledge chunks."""
    try:
        col = get_chroma_collection()
        count = col.count()
        if count == 0:
            return fallback_text_search(query, k)

        query_emb = await get_embedding(query)
        results = col.query(
            query_embeddings=[query_emb],
            n_results=min(k, count)
        )

        chunks = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            for doc, meta in zip(docs, metas):
                chunks.append({
                    "content": doc,
                    "source": meta.get("source", "knowledge_base"),
                    "topic": meta.get("topic", "General CCNA")
                })
        return chunks if chunks else fallback_text_search(query, k)
    except Exception:
        return fallback_text_search(query, k)


async def answer_rag_question(
    query: str,
    intent: str = "question",
    history: List[Dict[str, str]] | None = None
) -> Tuple[str, List[str]]:
    """Use local Cisco context when relevant while allowing natural Gemma conversation."""
    chunks = await search_knowledge(query, k=4) if is_network_question(query) else []
    sources = list(dict.fromkeys([c["source"] for c in chunks]))

    context_text = "\n\n".join(
        f"--- Source: {c['source']} ({c['topic']}) ---\n{c['content']}"
        for c in chunks
    )
    context_text = context_text[:9000]

    system_prompt = (
        "You are NetBuilder, powered by Gemma 4, embedded in a Cisco Packet Tracer "
        "and network protocol engineering application. Act as a senior network engineer, "
        "CCNA/CCNP instructor, and protocol developer. Answer any safe user request "
        "naturally, not only requests covered by the local knowledge base.\n\n"
        "For Packet Tracer lab and configuration requests, respond in this order: "
        "Overview; topology and cabling table; addressing table; complete per-device "
        "Cisco IOS configurations; verification commands and expected results; and "
        "two or three troubleshooting tips. Use real Packet Tracer models, interfaces, "
        "and commands. Never invent commands or claim that a .pkt file was created. "
        "If a feature is unsupported in Packet Tracer, say so and provide the closest "
        "supported alternative. If details are missing, make sensible assumptions and "
        "state them briefly before proceeding.\n\n"
        "For protocol, parser, simulator, or network-script requests, provide a brief "
        "design explanation followed by complete runnable code and run/test instructions. "
        "For troubleshooting, identify the likely root cause, explain it, and give the "
        "exact fix. Reply in the user's language while keeping commands and code in English. "
        "Use Markdown tables and fenced code blocks for labs and code.\n\n"
        "The local context below is optional reference material: use it when relevant, "
        "but do not limit answers to it. Be honest about uncertainty, do not claim "
        "internet access or actions you did not perform, and cite local source filenames "
        "when they materially support a Cisco answer."
    )

    conversation = []
    for message in (history or [])[-8:]:
        role = "assistant" if message.get("role") == "assistant" else "user"
        conversation.append({"role": role, "content": message["content"]})

    user_prompt = (
        f"OPTIONAL LOCAL CONTEXT (use only when relevant):\n{context_text or 'No matching local context was found.'}\n\n"
        f"USER REQUEST:\n{query}\n\n"
        f"ANSWER:"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        *conversation,
        {"role": "user", "content": user_prompt}
    ]

    try:
        reply = await ollama_client.chat(
            messages,
            temperature=0.1,
            timeout=180.0,
            num_predict=768
        )
    except Exception as e:
        reply = f"Error querying local model: {str(e)}"

    return reply, sources
