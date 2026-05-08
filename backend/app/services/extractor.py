import json
import os

import ollama
from dotenv import load_dotenv

load_dotenv()


OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2:1b")


PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "prompts")
SYSTEM_PROMPT_PATH = os.path.join(PROMPTS_DIR, "system_prompt.txt")


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
    Parse the JSON string returned by the LLM.

    Returns a dict with 'highlights' and 'pain_points' as lists of strings.
    Falls back to empty lists if the response is malformed so one bad review
    never crashes the whole request.
    """
    try:
        parsed = json.loads(raw)
        # Ensure both keys exist and are lists, even if the model omitted one.
        return {
            "highlights": parsed.get("highlights", []),
            "pain_points": parsed.get("pain_points", []),
        }
    except json.JSONDecodeError:
        print(f"[extractor] WARNING: LLM returned invalid JSON for review:\n  {review}\n  Raw response: {raw}")
        return {"highlights": [], "pain_points": []}


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