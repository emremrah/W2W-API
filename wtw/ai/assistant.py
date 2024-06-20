# type: ignore
import json
from typing import List

import json_repair
import requests
from loguru import logger
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from pydantic import BaseModel

from wtw.ai import config
from wtw.models import Movie


class AssistantResponse(BaseModel):
    """Response from the assistant."""

    title: str
    reason_to_watch: str


class Assistant:
    pass


class OpenAIAssistant(Assistant):
    prompt_base = """# genres
{}

# prompt
{}

# movies
{}"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    def _ask(self, prompt: str):

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "text": "You're an expert cinephile and you assist the questions with your recommendations.",
                            "type": "text",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "I will give you a list of movies and some information about user's taste. Then I will ask you to suggest movies from that list. I will give you:\n- A list of currently popular movies (in JSON format)\n- A list of genres the user likes (the list may be empty)\n- A prompt of user explaining what they like to watch at the moment\n\nThen you will return a list of movies in JSON format from the list with their names and a summary about what the user would love about the movie. The output must have the following keys:\ntitle: <the movie title>,\nreason_to_watch: the reasons why Ithe user would like this movie",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "# genres\n['Adventure', 'Biography', 'Documentary', 'Drama', 'Mystery', 'Thriller', 'War']\n\n# prompt\nI want a real war movie, I like immense battle scenes\n\n# movies\n[{'title': 'Bad Boys: Ride or Die', 'rating': 7.0, 'genres': ['Action', 'Adventure', 'Comedy', 'Crime', 'Thriller'], 'plot': \"This Summer, the world's favorite Bad Boys are back with their iconic mix of edge-of-your seat action and outrageous comedy but this time with a twist: Miami's finest are now on the run.\"}, {'title': 'Inside Out 2', 'rating': 8.0, 'genres': ['Animation', 'Adventure', 'Comedy', 'Drama', 'Family', 'Fantasy'], 'plot': 'Follows Riley, in her teenage years, encountering new emotions.'}, {'title': 'Furiosa: A Mad Max Saga', 'rating': 7.8, 'genres': ['Action', 'Adventure', 'Sci-Fi', 'Thriller'], 'plot': 'The origin story of renegade warrior Furiosa before her encounter and teamup with Mad Max.'}, {'title': 'Under Paris', 'rating': 5.2, 'genres': ['Action', 'Drama', 'Horror', 'Sport', 'Thriller'], 'plot': 'To save Paris from a bloodbath, a grieving scientist is forced to face her tragic past when a giant shark appears in the Seine.'}, {'title': 'The Watchers', 'rating': 5.8, 'genres': ['Fantasy', 'Horror', 'Mystery', 'Thriller'], 'plot': 'A young artist gets stranded in an extensive, immaculate forest in western Ireland, where, after finding shelter, she becomes trapped alongside three strangers, stalked by mysterious creatures each night.'}, {'title': 'The Fall Guy', 'rating': 7.0, 'genres': ['Action', 'Comedy', 'Drama'], 'plot': \"A down-and-out stuntman must find the missing star of his ex-girlfriend's blockbuster film.\"}, {'title': 'Godzilla Minus One', 'rating': 7.8, 'genres': ['Action', 'Adventure', 'Drama', 'Horror', 'Sci-Fi'], 'plot': 'Post-war Japan is at its lowest point when a new crisis emerges in the form of a giant monster, baptized in the horrific power of the atomic bomb.'}, {'title': 'Civil War', 'rating': 7.2, 'genres': ['Action', 'Adventure', 'Thriller'], 'plot': 'A journey across a dystopian future America, following a team of military-embedded journalists as they race against time to reach DC before rebel factions descend upon the White House.'}, {'title': 'Inside Out', 'rating': 8.1, 'genres': ['Animation', 'Adventure', 'Comedy', 'Drama', 'Family', 'Fantasy'], 'plot': 'After young Riley is uprooted from her Midwest life and moved to San Francisco, her emotions - Joy, Fear, Anger, Disgust and Sadness - conflict on how best to navigate a new city, house, and school.'}]",
                            "type": "text",
                        }
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": '```json\n[\n    {\n        "title": "Civil War",\n        "reason_to_watch": "This movie offers a thrilling journey across a dystopian future America with military-embedded journalists. The urgent race to reach DC before rebel factions take over promises intense action and war-like scenarios."\n    },\n    {\n        "title": "Godzilla Minus One",\n        "reason_to_watch": "While not a traditional war movie, its post-war Japan setting and the emergence of a giant monster metaphorically linked to the atomic bomb bring immense, catastrophic battle scenes that evoke the intensity of war."\n    }\n]\n```',
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt,
                            "type": "text",
                        }
                    ],
                },
            ],
            temperature=1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return response

    def ask_for_movies(self, prompt: str, genres: list, movies: list):
        prompt_final = self.prompt_base.format(genres, prompt, movies)
        logger.debug(prompt_final)
        response = self._ask(prompt_final)
        response_final = self.format_reponse(response)
        return response_final

    def format_reponse(self, response: ChatCompletion):
        response_text = response.choices[0].message.content
        if response_text is None:
            return []
        response_json = json_repair.loads(response_text)
        return [AssistantResponse(**item) for item in response_json]


class CustomAssistant(Assistant):
    prompt_base = """You are an expert cinephile and I need your help to recommend movies to a user.
    
You are given a set of favorite genres, the mood the user is in, and a list of movies. You are asked to recommend movies from the list that user would enjoy based on their favorite genres and prompt.
You MUST return a list of movies in the following JSON format:
```
[
    {{
        "title": "Movie Title",
        "reason_to_watch": "Reason to watch the movie"  // very brief reason to watch the movie. Explain why the user would enjoy the movie. Start with "You would enjoy this movie because..."
    }}
]
```

Favorite genres: {genres}
Prompt: {prompt}
Movies:
{movies}

Your answer:
```

"""

    def __init__(self, url: str = config.ASSISTANT_URL):
        self.assistant_url = url

    def _ask(self, prompt: str) -> requests.Response:
        """Ask the assistant a question."""
        response = requests.post(
            f"{self.assistant_url}/ask-llm", json={"prompt": prompt}
        )
        if response.status_code != 200:
            response.raise_for_status()

        return response

    def ask_for_movies(self, prompt: str, genres: list, movies: list):
        """Ask the assistant for movies."""
        prompt_final = self.prompt_base.format(
            genres=genres,
            prompt=prompt,
            movies=movies,
        )
        response = self._ask(prompt_final)
        response_model = self.format_reponse(response)
        return response_model

    def format_reponse(
        self, response: requests.Response
    ) -> List[AssistantResponse]:
        """Format the response from the assistant."""
        response_str: str = response.json()["response"]
        response_str = response_str.strip("`")
        response_json = json.loads(response_str)
        return [AssistantResponse(**item) for item in response_json]

    @staticmethod
    def format_movies(movies: List[Movie]):
        """Format the movies to be sent to the assistant."""
        fields = ["title", "rating", "genres", "plot"]
        movies_formatted = [
            {field: getattr(movie, field) for field in fields}
            for movie in movies
        ]
        return movies_formatted
