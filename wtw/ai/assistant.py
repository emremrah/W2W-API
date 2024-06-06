import json
from typing import List

import requests
from imdb.Movie import Movie
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from pydantic import BaseModel

from wtw.ai import config


class AssistantResponse(BaseModel):
    """Response from the assistant."""

    title: str
    reason_to_watch: str


class Assistant:
    pass


class OpenAIAssistant(Assistant):
    system_prompt = """You're my assistant and an expert in movies and TV shows. I will give you a list of movies and some information, then ask you to suggest me the movies that fit my taste from that list. I will give you:
- A list of currently popular movies (in JSON format)
- A list of genres I like. The list may be empty though.
- A prompt that explaining what I'd like to watch.

Then you will give me a list of movies in JSON format from the list with their names and a summary about what I would love about the movie. The output must follow this formatting:
```json
[
{{"name": <movie name>, "explanation": <the reasons why I'd like this movie>}},
...
]
```"""

    prompt_base = """Here we go:
# genres I like
{}

# my prompt
{}

# movies
```json
{}
```

Your answer:
```"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    def _ask(self, prompt: str) -> ChatCompletion:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        print(type(response))
        return response

    def ask_for_movies(
        self, prompt: str, genres: list, movies: list
    ) -> List[dict]:
        prompt_final = self.prompt_base.format(genres, prompt, movies)
        response = self._ask(prompt_final)
        response_final = self.format_reponse(response)
        return response_final

    def format_reponse(self, response: ChatCompletion):
        response_text = response.choices[0].message.content
        if response_text is None:
            return []
        return json.loads(response_text)


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
            {field: movie.get(field) for field in fields} for movie in movies
        ]
        return movies_formatted
