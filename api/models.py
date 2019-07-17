from typing import List, Dict, Union
from django.db import models
from api import tmdb


class Genre(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name
        }


class MovieQuerySet(models.QuerySet):
    def top(self, start_date: str, end_date: str, max_rank: int = None) -> List[Dict[str, Union[str, int]]]:
        top_movies = [{
            'movie_id': movie.id,
            'total_comments': movie.comment_set.filter(
                created_at__range=(f'{start_date}T00:00:00.000Z', f'{end_date}T23:59:59.999Z')
            ).count()
        } for movie in self]

        if top_movies:
            top_movies.sort(key=lambda movie: movie['total_comments'], reverse=True)
            current_min_total_comments = top_movies[0]['total_comments']
            current_rank = 1
            cutoff_index = len(top_movies)
            for current_index, movie in enumerate(top_movies):
                if movie['total_comments'] < current_min_total_comments:
                    current_rank += 1
                    current_min_total_comments = movie['total_comments']
                movie['rank'] = current_rank
                if max_rank and current_rank > max_rank:
                    cutoff_index = current_index
                    break

        return top_movies[:cutoff_index]


class MovieManager(models.Manager):
    def get_queryset(self):
        return MovieQuerySet(self.model, using=self._db)

    def update_or_create_from_tmdb(self, title: str) -> tuple:
        raw_movie = tmdb.fetch_movie(title)
        if not raw_movie:
            raise ValueError('no matching movie was found')
        movie, created = self.update_or_create(
            id=raw_movie['id'],
            overview=raw_movie['overview'],
            release_date=raw_movie['release_date'],
            original_title=raw_movie['original_title'],
            original_language=raw_movie['original_language'],
            title=raw_movie['title'],
            popularity=raw_movie['popularity'],
            vote_count=raw_movie['vote_count'],
            vote_average=raw_movie['vote_average'],
        )
        for genre_id in raw_movie['genre_ids']:
            try:
                genre = Genre.objects.get(id=genre_id)
            except Genre.DoesNotExist:
                pass
            else:
                movie.genres.add(genre)
        return movie, created


class Movie(models.Model):
    __SORTABLE_FIELDS = [
        'id', 'release_date', 'original_title', 'original_language', 'title', 'popularity', 'vote_count', 'vote_average'
    ]

    SORTABLE_FIELDS = __SORTABLE_FIELDS + [f'-{field}' for field in __SORTABLE_FIELDS]

    objects = MovieManager()

    id = models.PositiveIntegerField(primary_key=True)
    overview = models.TextField()
    release_date = models.DateField()
    genres = models.ManyToManyField(Genre, related_name='movies')
    original_title = models.CharField(max_length=1000)
    original_language = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    popularity = models.FloatField()
    vote_count = models.PositiveIntegerField()
    vote_average = models.FloatField()

    def __str__(self):
        return self.title

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'overview': self.overview,
            'release_date': self.release_date,
            'genres': [genre.to_dict() for genre in self.genres.all()],
            'original_title': self.original_title,
            'original_language': self.original_language,
            'title': self.title,
            'popularity': self.popularity,
            'vote_count': self.vote_count,
            'vote_average': self.vote_average
        }


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'created_at': self.created_at,
            'movie_id': self.movie.id,
            'text': self.text,
        }
