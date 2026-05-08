from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controller import router

app = FastAPI(
    title="Review Intelligence System",
    description="Extracts and deduplicates highlights and pain points from hotel reviews.",
    version="1.0.0",
)

# Allow the local React dev server to reach this API without CORS errors.
# In production we would lock this down to a specific origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health_check():
    """Quick liveness probe — useful for Docker health checks."""
    return {"status": "ok"}