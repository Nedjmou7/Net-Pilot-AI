import os
import sys
import asyncio
import chromadb
from chromadb.config import Settings

# Ensure parent directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.services.rag import search_knowledge


async def search(query: str, k: int = 4):
    results = await search_knowledge(query, k=k)
    return results


def main():
    if len(sys.argv) < 2:
        query = "How do I configure OSPF area 0 on a 2911 router?"
    else:
        query = " ".join(sys.argv[1:])

    print(f"Searching Cisco Knowledge Base for: '{query}'\n")
    results = asyncio.run(search(query, k=4))

    for idx, r in enumerate(results, 1):
        print(f"[{idx}] Source: {r.get('source')} (Topic: {r.get('topic')})")
        print(f"Snippet: {r.get('content')[:250]}...\n" + "-" * 50)


if __name__ == "__main__":
    main()
