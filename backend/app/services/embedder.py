import numpy as np
from sentence_transformers import SentenceTransformer

# ── Model ─────────────────────────────────────────────────────────────────────

# Load once at module level — SentenceTransformer takes a few seconds to
# initialise and we don't want that cost on every request.
# all-MiniLM-L6-v2: 80 MB, 384-dimensional vectors, fast and accurate enough
# for semantic similarity at this scale.
_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(texts: list[str]) -> np.ndarray:
    """
    Generate sentence embeddings for a list of strings.

    Args:
        texts: List of strings to embed.

    Returns:
        2-D numpy array of shape (len(texts), 384).
        Each row is the embedding vector for the corresponding string.
    """
    if not texts:
        return np.empty((0, 384), dtype="float32")

    # convert_to_numpy=True returns a plain ndarray ready for cosine_similarity.
    return _model.encode(texts, convert_to_numpy=True)