import json
import os

import ollama
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:1b")

# Resolve the path to the system prompt relative to this file so it works
# regardless of where uvicorn is launched from.
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "prompts")
SYSTEM_PROMPT_PATH = os.path.join(PROMPTS_DIR, "system_prompt.txt")

# ── Ollama client ─────────────────────────────────────────────────────────────

# Instantiate once at module level — avoids recreating the client on every call.
client = ollama.Client(host=OLLAMA_HOST)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_system_prompt() -> str:
    """Read the system prompt from disk. Raises clearly if the file is missing."""
    if not os.path.exists(SYSTEM_PROMPT_PATH):
        raise FileNotFoundError(
            f"System prompt not found at: {SYSTEM_PROMPT_PATH}\n"
            "Make sure backend/prompts/system_prompt.txt exists."
        )
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def _is_valid_item(item: str) -> bool:
    """
    Return False for items that are clearly LLM formatting artifacts rather
    than real extracted phrases — e.g. "[", ".", single characters, or
    strings that are just punctuation.
    """
    stripped = item.strip()
    if len(stripped) < 4:
        return False
    # Reject items that contain no letters at all
    if not any(c.isalpha() for c in stripped):
        return False
    return True


def _parse_llm_response(raw: str, review: str) -> dict:
    """
    Parse the JSON string returned by the LLM.

    Returns a dict with 'highlights' and 'pain_points' as lists of strings.
    Falls back to empty lists if the response is malformed so one bad review
    never crashes the whole request.
    """
    try:
        # Sometimes the model wraps the JSON in markdown fences — strip them.
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(cleaned)
        highlights = [i for i in parsed.get("highlights", []) if isinstance(i, str) and _is_valid_item(i)]
        pain_points = [i for i in parsed.get("pain_points", []) if isinstance(i, str) and _is_valid_item(i)]
        return {"highlights": highlights, "pain_points": pain_points}
    except json.JSONDecodeError:
        print(f"[extractor] WARNING: LLM returned invalid JSON for review:\n  {review}\n  Raw response: {raw}")
        return {"highlights": [], "pain_points": []}

# ── Public API ────────────────────────────────────────────────────────────────

def extract_from_review(review: str) -> dict:
    """
    Send a single review to the LLM and extract highlights and pain points.

    Args:
        review: A single hotel review string.

    Returns:
        {
            "highlights":  ["...", "..."],
            "pain_points": ["...", "..."],
        }
    """
    system_prompt = _load_system_prompt()

    response = client.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": f"Analyze this review:\n\n{review}"},
        ],
        format="json",
        options={"temperature": 0.1},  # low temperature for consistent, factual extraction
    )

    raw_content = response["message"]["content"]
    return _parse_llm_response(raw_content, review)