import re
from typing import Literal

IntentType = Literal["build", "question", "troubleshoot"]

BUILD_KEYWORDS = [
    r"\bbuild\b", r"\bcreate\b", r"\bdesign\b", r"\bgenerate\b", r"\bsetup\b",
    r"\bset up\b", r"\btopology\b", r"\badd\b", r"\bconnect\b", r"\bconfigure a network\b",
    r"\bnetwork with\b", r"\brouters?\b", r"\bswitches?\b", r"\bvlan\b"
]

TROUBLESHOOT_KEYWORDS = [
    r"\bwhy\b", r"\bcan'?t ping\b", r"\bcannot ping\b", r"\bfail\b", r"\bfailed\b",
    r"\berror\b", r"\btroubleshoot\b", r"\bdebug\b", r"\bunreachable\b",
    r"\bdown\b", r"\bbroken\b", r"\bpacket drop\b", r"\bno route\b"
]


def classify_intent_rules(message: str) -> IntentType:
    lower = message.lower()

    # Troubleshoot has high priority if user states an issue/error
    for pattern in TROUBLESHOOT_KEYWORDS:
        if re.search(pattern, lower):
            return "troubleshoot"

    # Build requests
    for pattern in BUILD_KEYWORDS:
        if re.search(pattern, lower):
            return "build"

    # Default to question if it's general explanation
    return "question"


async def classify_intent(message: str) -> IntentType:
    """Classify user intent using fast rule matching with fallback."""
    return classify_intent_rules(message)
