import json


def ask_openai(movie_titles):
    return json.dumps(
        {
            t: {
                "title": t,
                "explanation": "The quick brown fox jumps over the lazy dog",
            }
            for t in movie_titles
        }
    )
