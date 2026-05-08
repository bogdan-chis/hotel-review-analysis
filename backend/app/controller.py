from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models import ProcessFileResponse
from app.services.extractor import extract_from_review
from app.services.deduplicator import deduplicate

router = APIRouter()


@router.post("/process_file", response_model=ProcessFileResponse)
async def process_file(file: UploadFile = File(...)) -> ProcessFileResponse:
    """
    Accepts a .txt file (one review per line).

    Pipeline:
        1. Read and split the file into individual reviews.
        2. For each review, call the LLM to extract highlights and pain points.
        3. Aggregate all highlights into one list, all pain points into another.
        4. Deduplicate each list via cosine similarity.
        5. Return the final structured response.
    """
    try:
        content = await file.read()
        raw_text = content.decode("utf-8")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read the uploaded file. Make sure it is a UTF-8 encoded .txt file.")

    # Split on newlines and discard blank lines.
    reviews = [line.strip() for line in raw_text.splitlines() if line.strip()]

    if not reviews:
        raise HTTPException(status_code=400, detail="The uploaded file contains no reviews.")

    all_highlights: list[str] = []
    all_pain_points: list[str] = []

    for review in reviews:
        extracted = extract_from_review(review)
        all_highlights.extend(extracted["highlights"])
        all_pain_points.extend(extracted["pain_points"])

    deduplicated_highlights = deduplicate(all_highlights)
    deduplicated_pain_points = deduplicate(all_pain_points)

    return ProcessFileResponse(
        highlights=deduplicated_highlights,
        pain_points=deduplicated_pain_points,
    )