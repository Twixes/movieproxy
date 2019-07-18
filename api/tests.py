import json
from typing import Dict
from django.test import TestCase
from api.models import Genre, Movie, Comment
from api.views import movies, comments, top


class DummyRequest:
    def __init__(self, *, GET: Dict[str, str] = None, POST: Dict[str, str] = None):
        if GET is not None:
            self.method = 'GET'
            self.GET = GET
        elif POST is not None:
            self.method = 'POST'
            self.POST = POST


class EndpointsTestCase(TestCase):
    def test_add_movie(self):
        response = movies(DummyRequest(POST={'title': 'godfather'}))
        expected_response_data = {
            'id': 238,
            'overview': (
                'Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime '
                'family. When organized crime family patriarch, Vito Corleone barely survives an attempt on '
                'his life, his youngest son, Michael steps in to take care of the would-be killers, launching '
                'a campaign of bloody revenge.'
            ),
            'release_date': '1972-03-14',
            'genres': [{'id': 18,'name': 'Drama'}, {'id': 80, 'name': 'Crime'}],
            'original_title': 'The Godfather',
            'original_language': 'en',
            'title': 'The Godfather'
        }
        actual_response_data = json.loads(response.getvalue())
        self.assertEqual(response.status_code, 201)
        for key in expected_response_data:
            self.assertEqual(actual_response_data[key], expected_response_data[key])

    def test_get_movie(self):
        Movie.objects.update_or_create_from_tmdb('godfather')
        response = movies(DummyRequest(GET={'title': 'godfather'}))
        expected_response_data = {
            'id': 238,
            'overview': (
                'Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime '
                'family. When organized crime family patriarch, Vito Corleone barely survives an attempt on '
                'his life, his youngest son, Michael steps in to take care of the would-be killers, launching '
                'a campaign of bloody revenge.'
            ),
            'release_date': '1972-03-14',
            'genres': [{'id': 18,'name': 'Drama'}, {'id': 80, 'name': 'Crime'}],
            'original_title': 'The Godfather',
            'original_language': 'en',
            'title': 'The Godfather'
        }
        actual_response_data = json.loads(response.getvalue())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(actual_response_data), 1)
        for key in expected_response_data:
            self.assertEqual(actual_response_data[0][key], expected_response_data[key])

    def test_add_coment(self):
        Movie.objects.update_or_create_from_tmdb('godfather')
        response = comments(DummyRequest(POST={'movie_id': '238', 'text': 'Tremendous'}))
        expected_response_data = {
            'id': 1,
            'movie_id': 238,
            'text': 'Tremendous'
        }
        actual_response_data = json.loads(response.getvalue())
        self.assertEqual(response.status_code, 201)
        for key in expected_response_data:
            self.assertEqual(actual_response_data[key], expected_response_data[key])

    def test_get_coment(self):
        Movie.objects.update_or_create_from_tmdb('godfather')
        Comment.objects.create(movie_id=238, text='Tremendous')
        response = comments(DummyRequest(GET={'movie_id': '238'}))
        expected_response_data = {
            'id': 1,
            'movie_id': 238,
            'text': 'Tremendous'
        }
        actual_response_data = json.loads(response.getvalue())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(actual_response_data), 1)
        for key in expected_response_data:
            self.assertEqual(actual_response_data[0][key], expected_response_data[key])

    def test_get_top(self):
        Movie.objects.update_or_create_from_tmdb('godfather')
        Movie.objects.update_or_create_from_tmdb('frozen')
        Comment.objects.create(movie_id=238, text='Tremendous')
        response = top(DummyRequest(GET={'start_date': '1970-01-01', 'end_date': '2070-01-01'}))
        expected_response_data = [
            {
                'movie_id': 238,
                'total_comments': 1,
                'rank': 1
            },
            {
                'movie_id': 109445,
                'total_comments': 0,
                'rank': 2
            }
        ]
        actual_response_data = json.loads(response.getvalue())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(actual_response_data, expected_response_data)
