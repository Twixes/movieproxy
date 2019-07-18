from typing import Sequence
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.db.utils import IntegrityError
from api.models import Movie, Comment


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
                f'Value \'{value_attempted}\' is not valid for field \'{field_attempted}\''
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
        if not request.POST.get('title'):
            return generate_mandatory_field_missing_response('title')
        try:
            movie, created = Movie.objects.update_or_create_from_tmdb(request.POST['title'])
        except ValueError:
            return generate_resource_not_found_response('movie')
        else:
            return JsonResponse(movie.to_dict(), status=201 if created else 200)

    elif request.method == 'GET':
        movies = Movie.objects.all()
        # optionally filter
        if request.GET.get('title'):
            movies = (
                movies.filter(title__icontains=request.GET['title']) |
                movies.filter(original_title__icontains=request.GET['title'])
            )
        # optionally order
        if request.GET.get('order_by'):
            order_by_fields = [field.strip() for field in request.GET['order_by'].strip(',').split(',')]
            for field in order_by_fields:
                if field not in Movie.SORTABLE_FIELDS:
                    return generate_invalid_field_value_response(
                        'order_by', field, 'not a sortable movie field'
                    )
            if order_by_fields:
                movies = movies.order_by(*order_by_fields)
        return JsonResponse([movie.to_dict() for movie in movies], safe=False)

    else:
        return generate_method_not_allowed_response(request.method, ('GET', 'POST'))


def comments(request) -> JsonResponse:
    if request.method == 'POST':
        # check if required fields are present
        if not request.POST.get('movie_id'):
            return generate_mandatory_field_missing_response('movie_id')
        if not request.POST.get('text'):
            return generate_mandatory_field_missing_response('text')
        try:
            comment = Comment.objects.create(movie_id=request.POST['movie_id'], text=request.POST['text'])
        except IntegrityError:
            return generate_invalid_field_value_response(
                'movie_id', request.POST['movie_id'], 'movie not in database'
            )
        else:
            return JsonResponse(comment.to_dict(), status=201)

    elif request.method == 'GET':
        comments = Comment.objects.all()
        # optionally filter
        if request.GET.get('movie_id'):
            try:
                comments = comments.filter(movie_id=request.GET['movie_id'])
            except ValueError:
                return generate_invalid_field_value_response('movie_id', request.GET['movie_id'])
        return JsonResponse([comment.to_dict() for comment in comments], safe=False)

    else:
        return generate_method_not_allowed_response(request.method, ('GET', 'POST'))


def top(request) -> JsonResponse:
    if request.method == 'GET':
        # check if required fields are present
        if not request.GET.get('start_date'):
            return generate_mandatory_field_missing_response('start_date')
        if not request.GET.get('end_date'):
            return generate_mandatory_field_missing_response('end_date')
        max_rank = None
        if request.GET.get('max_rank'):
            try:
                max_rank = int(request.GET['max_rank'])
            except ValueError:
                return generate_invalid_field_value_response('max_rank', request.GET['max_rank'], 'must be an integer')
        try:
            top = Movie.objects.all().top(request.GET['start_date'], request.GET['end_date'], max_rank)
        except ValidationError as e:
            # check from which date paramater does the error stem
            if e.params['value'].startswith(request.GET['start_date']):
                return generate_invalid_field_value_response('start_date', request.GET['start_date'])
            else:
                return generate_invalid_field_value_response('end_date', request.GET['end_date'])

        else:
            return JsonResponse(top, safe=False)

    else:
        return generate_method_not_allowed_response(request.method, ('GET',))
