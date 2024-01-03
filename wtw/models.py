from typing import List, Optional, Union

from pydantic import BaseModel


class Top100Request:
    class Request(BaseModel):
        genres: List[str] = []
        min_rating: Union[int, float] = 0
        search_in: int = 100
        use_ai: bool = False
        user_prompt: Optional[str] = None


class MovieModel(BaseModel):
    id: str
    title: str
    plot: Optional[str]
    rating: Optional[float]
    genres: Optional[List[str]]
    image_url: Optional[str] = None
    imdb_url: Optional[str] = None
    ai_summary: Optional[str] = None
