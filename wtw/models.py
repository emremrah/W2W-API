from typing import List, Optional

from pydantic import BaseModel


class Movie(BaseModel):
    id: Optional[str] = None
    title: str
    plot: Optional[str] = None
    genres: List[str] = []
    rating: Optional[float] = None
    image_url: Optional[str] = None
    imdb_url: Optional[str] = None
    ai_summary: Optional[str] = None

    class Config:
        extra = "allow"
