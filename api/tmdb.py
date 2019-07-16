import os
from typing import Optional, List
import requests

API_KEY = os.environ['TMDB_API_KEY']
API_BASE_URL = 'https://api.themoviedb.org/3'
HEADERS = { 'User-Agent': 'MovieProxy' }


def fetch_movie(title: str) -> Optional[dict]:
    """Fetch the movie with the the closest matching title (if one exists)."""
    params = {'api_key': API_KEY, 'query': title}
    response = requests.get(
        f'{API_BASE_URL}/search/movie', headers=HEADERS, params=params
    ).json()
    if response['results']:
        return response['results'][0]
    else:
        return None


def fetch_genres() -> List[dict]:
    """Fetch all genres."""
    params = {'api_key': API_KEY}
    response = requests.get(f'{API_BASE_URL}/genre/movie/list', headers=HEADERS, params=params).json()
    return response['genres']
