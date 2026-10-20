import re
import json
import logging
from typing import Literal
from app.services.ollama_client import ollama_client

logger = logging.getLogger("topogemma.intent")

BUILD_KEYWORDS = [
    r"\bbuild\b", r"\bcreate\b", r"\bdesign\b", r"\bgenerate\b", r"\bmake a network\b",
    r"\bsetup\b", r"\bset up\b", r"\btopology\b", r"\brouters?\b", r"\bswitches?\b",
    r"\bvlans?\b", r"\bospf\b", r"\binter-vlan\b", r"\bdhcp\b", r"\badd\b", r"\bconnect\b"
]

TROUBLESHOOT_KEYWORDS = [
    r"can'?t\s+ping", r"cannot\s+ping", r"fail", r"error", r"troubleshoot",
    r"why\s+(is|are|does|doesn't|isn't|can't)", r"not\s+working", r"unreachable",
    r"show\s+run", r"show\s+ip", r"debug", r"packet\s+loss", r"timeout"
]

QUESTION_KEYWORDS = [
    r"what\s+is", r"how\s+(does|do|to)", r"explain", r"difference\s+between",
    r"meaning\s+of", r"tell\s+me\s+about", r"which\s+command", r"what\s+does"
]

def rule_based_intent(text: str) -> Literal["build", "question", "troubleshoot"]:
    text_lower = text.lower().strip()

    # Troubleshoot has high specificity
    for pattern in TROUBLESHOOT_KEYWORDS:
        if re.search(pattern, text_lower):
            return "troubleshoot"

    # Build requests
    build_matches = sum(1 for p in BUILD_KEYWORDS if re.search(p, text_lower))
    question_matches = sum(1 for p in QUESTION_KEYWORDS if re.search(p, text_lower))

    if build_matches > 0 and (re.search(r"\b(build|create|design|setup|generate)\b", text_lower) or build_matches >= 2):
        return "build"

    if question_matches > 0:
        return "question"

    if build_matches > 0:
        return "build"

    return "question"

async def classify_intent(message: str) -> Literal["build", "question", "troubleshoot"]:
    """Classify the user intent using LLM if available, fallback to keyword rules."""
    rule_intent = rule_based_intent(message)

    # If strongly matched by keywords, return immediately for instant latency
    msg_lower = message.lower()
    if any(re.search(p, msg_lower) for p in [r"\bbuild\b", r"\bcreate\b", r"can'?t\s+ping"]):
        return rule_intent

    # Otherwise try LLM classification
    try:
        prompt = (
            "Classify the following user message into exactly ONE category: 'build', 'question', or 'troubleshoot'.\n"
            "- 'build': User wants to generate or construct a network topology or lab.\n"
            "- 'question': User asks an educational or conceptual question about Cisco/networking.\n"
            "- 'troubleshoot': User has an issue, broken network, ping failure, or error they want to solve.\n\n"
            f"Message: \"{message}\"\n\n"
            "Output JSON with format: {\"intent\": \"build\" | \"question\" | \"troubleshoot\"}"
        )
        res = await ollama_client.chat(
            messages=[{"role": "user", "content": prompt}],
            format_json=True,
            temperature=0.0
        )
        content = res.get("message", {}).get("content", "").strip()
        parsed = json.loads(content)
        intent = parsed.get("intent", "").lower()
        if intent in ["build", "question", "troubleshoot"]:
            return intent
    except Exception as e:
        logger.debug(f"LLM intent classification fallback due to: {e}")

    return rule_intent
