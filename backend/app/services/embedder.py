import numpy as np
from sentence_transformers import SentenceTransformer



_model = SentenceTransformer("BAAI/bge-small-en-v1.5")

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