import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.models import ReviewItem
from app.services.embedder import embed

SIMILARITY_THRESHOLD = 0.8


def deduplicate(items: list[str]) -> list[ReviewItem]:
    """
    Collapse semantically similar strings into one representative item,
    recording how many duplicates each representative absorbed.

    Algorithm:
        1. Embed all items into vectors.
        2. Compute an NxN cosine similarity matrix.
        3. Iterate through items in order. For each unvisited item, find all
           other unvisited items whose similarity to it exceeds the threshold —
           that forms one group.
        4. The first item in the group becomes the representative; count = group size.
        5. All other group members are marked visited so they are skipped.

    Args:
        items: Flat list of extracted strings (e.g. all highlights across all reviews).

    Returns:
        List of ReviewItem(item=..., count=...) with duplicates removed.
    """
    if not items:
        return []

    # Step 1 — embed
    vectors = embed(items)

    # Step 2 — N×N similarity matrix
    # Shape: (n, n) where sim_matrix[i][j] is the cosine similarity of items i and j.
    sim_matrix = cosine_similarity(vectors)

    visited = set()
    results: list[ReviewItem] = []

    # Step 3 — greedy grouping
    for i, representative in enumerate(items):
        if i in visited:
            continue

        # Find all unvisited items (including i itself) similar enough to i.
        group = [
            j for j in range(len(items))
            if j not in visited and sim_matrix[i][j] > SIMILARITY_THRESHOLD
        ]

        # Step 4 — record the representative with its count
        results.append(ReviewItem(item=representative, count=len(group)))

        # Step 5 — mark every group member as visited
        visited.update(group)

    return results