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
    def top(self) -> List[Dict[str, Union[str, int]]]:
        top_movies = [{
            'movie_id': movie.id,
            'total_comments': movie.comment_set.count()
        } for movie in self]
        if top_movies:
            top_movies.sort(key=lambda movie: movie['total_comments'], reverse=True)

            current_min_total_comments = top_movies[0]['total_comments']
            current_rank = 1
            for movie in top_movies:
                if movie['total_comments'] < current_min_total_comments:
                    current_rank += 1
                    current_min_total_comments = movie['total_comments']
                movie['rank'] = current_rank

        return top_movies


class MovieManager(models.Manager):
    def get_queryset(self):
        return MovieQuerySet(self.model, using=self._db)

    def update_or_create_from_tmdb(self, title: str) -> tuple:
        raw_movie = tmdb.fetch_movie(title)
        if not raw_movie:
            raise ValueError('no matching movie was found')
        genre_ids = raw_movie.pop('genre_ids')
        movie, created = self.update_or_create(**raw_movie)
        for genre_id in genre_ids:
            try:
                genre = Genre.objects.get(id=genre_id)
            except Genre.DoesNotExist:
                pass
            else:
                movie.genres.add(genre)
        return movie, created


class Movie(models.Model):
    SORTABLE_FIELDS = [
        'id', 'adult', 'release_date', 'original_title', 'original_language', 'title', 'popularity', 'vote_count',
        'video', 'vote_average'
    ]

    objects = MovieManager()

    id = models.PositiveIntegerField(primary_key=True)
    poster_path = models.CharField(max_length=1000, null=True)
    adult = models.BooleanField()
    overview = models.TextField()
    release_date = models.DateField()
    genres = models.ManyToManyField(Genre, related_name='movies')
    original_title = models.CharField(max_length=1000)
    original_language = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    backdrop_path = models.CharField(max_length=1000, null=True)
    popularity = models.FloatField()
    vote_count = models.PositiveIntegerField()
    video = models.BooleanField()
    vote_average = models.FloatField()

    def __str__(self):
        return self.title

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'poster_path': self.poster_path,
            'adult': self.adult,
            'overview': self.overview,
            'release_date': self.release_date,
            'genre_ids': [genre.id for genre in self.genres.all()],
            'original_title': self.original_title,
            'original_language': self.original_language,
            'title': self.title,
            'backdrop_path': self.backdrop_path,
            'popularity': self.popularity,
            'vote_count': self.vote_count,
            'video': self.video,
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
