from typing import List, Optional, Union
from wtw.models import Movie
from pydantic import BaseModel


class Top100Movie:
    class Request(BaseModel):
        genres: List[str] = []
        min_rating: Union[int, float] = 0
        search_in: int = 10
        use_ai: bool = False
        user_prompt: Optional[str] = None

    class Response(BaseModel):
        movies: List[Movie]
