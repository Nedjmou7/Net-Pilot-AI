import os
import re
import math
import hashlib
from typing import List, Dict, Any
import httpx
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

def compute_offline_vector(text: str, dim: int = 128) -> List[float]:
    """
    Computes a 100% local, offline, deterministic dense embedding vector
    using term frequency, keyword weighting, and salted hashing.
    No network downloads or external weights required.
    """
    words = re.findall(r"\w+", text.lower())
    vec = [0.0] * dim

    # Key CCNA terms get higher weights
    high_weight_keywords = {
        "ospf": 4.0, "vlan": 4.0, "router": 3.0, "switch": 3.0, "subnet": 3.5,
        "ping": 4.0, "gateway": 4.0, "dhcp": 4.0, "nat": 4.0, "pat": 4.0,
        "acl": 4.0, "trunk": 3.5, "access": 3.0, "crossover": 3.0, "straight": 3.0,
        "interface": 2.5, "gigabitethernet": 3.0, "fastethernet": 3.0, "ip": 2.0,
        "route": 3.0, "static": 3.0, "rip": 3.5, "eigrp": 3.5, "spanning": 3.5,
        "portfast": 3.5, "bpduguard": 3.5, "etherchannel": 3.5, "ssh": 3.5
    }

    for w in words:
        weight = high_weight_keywords.get(w, 1.0)
        # Hash word to multiple dimensions to reduce collisions
        h1 = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16) % dim
        h2 = int(hashlib.sha1(w.encode("utf-8")).hexdigest(), 16) % dim
        vec[h1] += weight
        vec[h2] += weight * 0.5

    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec

class LocalRobustEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.ollama_available = self._probe_ollama()

    def _probe_ollama(self) -> bool:
        try:
            with httpx.Client(timeout=1.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name", "") for m in res.json().get("models", [])]
                    return any(self.model_name in m for m in models)
        except Exception:
            pass
        return False

    def __call__(self, input: Documents) -> Embeddings:
        if self.ollama_available:
            try:
                embeddings = []
                with httpx.Client(timeout=10.0) as client:
                    for text in input:
                        res = client.post(
                            f"{self.base_url}/api/embeddings",
                            json={"model": self.model_name, "prompt": text}
                        )
                        if res.status_code == 200:
                            embeddings.append(res.json().get("embedding"))
                        else:
                            raise RuntimeError()
                return embeddings
            except Exception:
                self.ollama_available = False

        # 100% offline deterministic embedding
        return [compute_offline_vector(text) for text in input]
