from typing import List
from django.db import models

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
    def top(self) -> List[dict]:
        print(self)
        top_movies = [{
            'movie_id': movie.id,
            'total_comments': movie.comment_set.count()
        } for movie in self]

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

    def pdfs(self):
        return self.get_queryset().pdfs()

    def smaller_than(self, size):
        return self.get_queryset().smaller_than(size)


class Movie(models.Model):
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
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'movie_id': self.movie.id,
            'text': self.text
        }
