from typing import Sequence
from django.http import HttpResponse, JsonResponse
from django.db.utils import IntegrityError
from .models import Movie, Genre, Comment
from api import tmdb

TEST_RESPONSE = { 'abc': 'xyz' }
MOVIE_FIELDS = [field.name for field in Movie._meta.get_fields()]


def generate_resource_not_found_response(resource_type: str) -> JsonResponse:
    """Generate a 404 error response."""
    return JsonResponse(
        { 'error': f'No matching {resource_type} was found' },
        status=404
    )


def generate_method_not_allowed_response(method_attempted: str, methods_allowed: Sequence[str]) -> JsonResponse:
    """Generate a 405 error response."""
    return JsonResponse(
        { 'error': f'Method {method_attempted} is not allowed, only {", ".join(methods_allowed)}' },
        status=405
    )

def generate_mandatory_field_missing_response(field_missing: str) -> JsonResponse:
    """Generate a 422 error response."""
    return JsonResponse(
        { 'error': f'Mandatory field \'{field_missing}\' is missing' },
        status=422
    )

def generate_invalid_field_value_response(
        field_attempted: str, value_attempted: str, reason: str = None
) -> JsonResponse:
    """Generate a 422 error response."""
    return JsonResponse(
        {
            'error': (
                f'Value {value_attempted} is not valid for field {field_attempted}'
                f'{f" ({reason})" if reason else ""}'
            )
        },
        status=422
    )


def welcome(request) -> HttpResponse:
    return HttpResponse("Welcome to MovieProxy")


def movies(request) -> JsonResponse:
    if request.method == 'POST':
        # check if required field is present
        if 'title' not in request.POST:
            return generate_resource_not_found_response('movie')
        raw_movie = tmdb.fetch_movie(request.POST.get('title'))
        if raw_movie:
            genre_ids = raw_movie.pop('genre_ids')
            movie, created = Movie.objects.update_or_create(**raw_movie)
            for genre_id in genre_ids:
                try:
                    genre = Genre.objects.get(id=genre_id)
                except Genre.DoesNotExist:
                    pass
                else:
                    movie.genres.add(genre)
            return JsonResponse(movie.to_dict(), status=201 if created else 200)
        else:
            return generate_mandatory_field_missing_response('title')

    elif request.method == 'GET':
        movies = Movie.objects.all()
        # optionally order
        if 'order_by' in request.GET:
            if request.GET.get('order_by') in MOVIE_FIELDS:
                movies = movies.order_by(request.GET.get('order_by'))
            else:
                return generate_invalid_field_value_response('order_by', request.GET.get('order_by'))
        return JsonResponse([movie.to_dict() for movie in movies], safe=False)

    else:
        return generate_method_not_allowed_response(request.method, ('GET', 'POST'))

def comments(request) -> JsonResponse:
    if request.method == 'POST':
        # check if required fields are present
        if 'movie_id' not in request.POST:
            return generate_mandatory_field_missing_response('movie_id')
        if 'text' not in request.POST:
            return generate_mandatory_field_missing_response('text')
        try:
            comment = Comment.objects.create(movie_id=request.POST.get('movie_id'), text=request.POST.get('text'))
        except IntegrityError:
            return generate_invalid_field_value_response(
                'movie_id', request.POST.get('movie_id'), 'movie not in database'
            )
        else:
            return JsonResponse(comment.to_dict(), status=201)

    elif request.method == 'GET':
        comments = Comment.objects.all()
        # optionally filter
        if 'movie_id' in request.GET:
            try:
                comments = comments.filter(movie_id=request.GET.get('movie_id'))
            except ValueError:
                return generate_invalid_field_value_response('movie_id', request.GET.get('movie_id'))
        return JsonResponse([comment.to_dict() for comment in comments], safe=False)

    else:
        return generate_method_not_allowed_response(request.method, ('GET', 'POST'))


def top(request) -> JsonResponse:
    if request.method == 'GET':
        movies = Movie.objects.all()
        # check if required fields are present
        if 'after' not in request.GET:
            return generate_mandatory_field_missing_response('after')
        if 'before' not in request.GET:
            return generate_mandatory_field_missing_response('before')
        try:
            movies = movies.filter(release_date__gt=request.GET.get('after'))
        except ValueError:
            return generate_invalid_field_value_response('after', request.GET.get('after'))
        try:
            movies = movies.filter(release_date__lt=request.GET.get('before'))
        except ValueError:
            return generate_invalid_field_value_response('before', request.GET.get('before'))
        return JsonResponse(movies.top(), safe=False)

    else:
        return generate_method_not_allowed_response(request.method, ('GET',))
