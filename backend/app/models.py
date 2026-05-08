from pydantic import BaseModel


class ReviewItem(BaseModel):
    """A single deduplicated insight with how many similar items it absorbed."""
    item: str
    count: int


class ProcessFileResponse(BaseModel):
    """The final API response returned by POST /process_file."""
    highlights: list[ReviewItem]
    pain_points: list[ReviewItem]