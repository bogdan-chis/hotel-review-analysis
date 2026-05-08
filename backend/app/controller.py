from fastapi import APIRouter, UploadFile, File

from app.models import ProcessFileResponse, ReviewItem

router = APIRouter()


@router.post("/process_file", response_model=ProcessFileResponse)
async def process_file(file: UploadFile = File(...)) -> ProcessFileResponse:
    """
    Accepts a .txt file (one review per line) and returns deduplicated
    highlights and pain points.

    NOTE: This is a stub — real service calls will be wired in Step 5.
    """
    # --- stub: ignore the file and return hardcoded dummy data ---
    return ProcessFileResponse(
        highlights=[
            ReviewItem(item="Room was very clean", count=2),
            ReviewItem(item="Breakfast was excellent", count=2),
            ReviewItem(item="Amazing location near the beach", count=1),
            ReviewItem(item="Staff were friendly", count=1),
        ],
        pain_points=[
            ReviewItem(item="Check-in took too long", count=3),
        ],
    )