import json
import os

import ollama
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:1b")

# Resolve the path to the system prompt relative to this file so it works
# regardless of where uvicorn is launched from.
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "prompts")
SYSTEM_PROMPT_PATH = os.path.join(PROMPTS_DIR, "system_prompt.txt")


# Instantiate once at module level — avoids recreating the client on every call.
client = ollama.Client(host=OLLAMA_HOST)


def _load_system_prompt() -> str:
    """Read the system prompt from disk. Raises clearly if the file is missing."""
    if not os.path.exists(SYSTEM_PROMPT_PATH):
        raise FileNotFoundError(
            f"System prompt not found at: {SYSTEM_PROMPT_PATH}\n"
            "Make sure backend/prompts/system_prompt.txt exists."
        )
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()

def _parse_llm_response(raw: str, review: str) -> dict:
    """
    Parses the JSON string returned by the SLM.

    Returns a dict with 'highlights' and 'pain_points' as lists of strings.
    Falls back to empty lists if the response is malformed so one bad review
    never crashes the whole request.
    """
    try:
        # Sometimes the model wraps the JSON in markdown fences — strip them.
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(cleaned)
        highlights = [i for i in parsed.get("highlights", []) if isinstance(i, str)]
        pain_points = [i for i in parsed.get("pain_points", []) if isinstance(i, str)]
        return {"highlights": highlights, "pain_points": pain_points}
    except json.JSONDecodeError:
        print(f"[extractor] WARNING: LLM returned invalid JSON for review:\n  {review}\n  Raw response: {raw}")
        return {"highlights": [], "pain_points": []}

def extract_from_review(review: str) -> dict:
    """
    Sends a single review to the SLM and extract highlights and pain points.
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
        options={"temperature": 0.1},
    )

    raw_content = response["message"]["content"]
    return _parse_llm_response(raw_content, review)