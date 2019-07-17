# MovieProxy


A simple Django REST API.


## Objects

### Genre

field | type    | description
----- | ------- | -----------
id    | integer | genre ID
name  | string  | genre name

##### Example
```JSON
{
    "id": 12,
    "name": "Adventure"
}
```

### Movie

field             | type                   | description
----------------- | ---------------------- | -----------------------------------------------
id                | id                     | movie ID
overview          | string                 | movie overview
release_date      | string                 | movie release date in ISO format
genres            | array of genre objects | IDs of genres the movie is associated with
original_title    | string                 | movie title in original language
original_language | string                 | original movie language code
title             | string                 | movie title
popularity        | number                 | movie popularity score
vote_count        | integer                | number of votes gathered by movie on TMDb
vote_average      | number                 | movie vote average on TMDb

##### Example
```JSON
{
    "id": 238,
    "poster_path": "/rPdtLWNsZmAtoZl9PK7S2wE3qiS.jpg",
    "adult": false,
    "overview": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone barely survives an attempt on his life, his youngest son, Michael steps in to take care of the would-be killers, launching a campaign of bloody revenge.",
    "release_date": "1972-03-14",
    "genres": [
        { "id": 80, "name": "Crime" },
        { "id": 18, "name": "Drama" }
    ],
    "original_title": "The Godfather",
    "original_language": "en",
    "title": "The Godfather",
    "backdrop_path": "/6xKCYgH16UuwEGAyroLU6p8HLIn.jpg",
    "popularity": 26.961,
    "vote_count": 10216,
    "video": false,
    "vote_average": 8.6
}
```

### Comment

field      | type    | description
---------- | ------- | ----------------------------------------------
id         | integer | comment ID
created_at | string  | comment creation timestmap in ISO format
movie_id   | integer | ID of the movie the comment is associated with
text       | string  | comment body

##### Example
```JSON
{
    "id": 1024,
    "created_at": "2019-07-07T21:37:69.420Z",
    "movie_id": 109445,
    "text": "An abomination, worse than The Room"
}
```

### Error

field | type   | description
----- | ------ | -------------
error | string | error message

##### Example
```JSON
{
    "error": "Mandatory field 'title' is missing"
}
```


## Endpoints

### Get Movie
#### GET `/movies`

##### Request – `application/x-www-form-urlencoded` (query string)
field     | type   | description
--------- | ------ | ------------------------------------------------------
?title    | string | title fragment to be matched
?order_by | string | comma-separated list of fields to order the results by

##### Response – `application/json`
`200` and an array of matching movie objects or `422` and an error object.

### Add Movie
#### POST `/movies`

##### Request – `application/x-www-form-urlencoded`
field | type   | description
----- | ------ | ----------------------------
title | string | title fragment to be matched

##### Response – `application/json`
`200`/`201` and the matching movie object or `404`/`422` and an error object.

### Get Comment
#### GET `/comments`

##### Request – `application/x-www-form-urlencoded` (query string)
field     | type    | description
--------- | ------- | -------------------------------------------------------------
?movie_id | integer | ID of the movie the fetched comments shall be associated with

##### Response – `application/json`
`200` and an array of matching comment objects or `422` and an error object.

### Add Comment
#### POST `/comments`

##### Request – `application/x-www-form-urlencoded`
field    | type    | description
-------- | ------- | ----------------------------------------------------
movie_id | integer | ID of the movie the comment shall be associated with
text     | string  | comment body

##### Response – `application/json`
`201` and the created comment object or `422` and an error object.

### Get Top
#### GET `/top`

##### Request – `application/x-www-form-urlencoded` (query string)
field      | type    | description
---------- | ------- | ----------------------------------------------
start_date | string  | start date of the ranking period in ISO format
end_date   | string  | end date of the ranking period in ISO format
?max_rank  | integer | the maximum rank returned

##### Response – `application/json`
`200` and an array of matching comment objects or `422` and an error object.


## Running with Heroku

This is the easiest way to run MovieProxy.

Create a Heroku app, connect this repository to it and, in the Settings tab, add the following config vars to it:

* `DISABLE_COLLECTSTATIC` – set this to `1` to disable a Heroku feature that would be problematic in this case
* `ALLOWED_HOSTS` – a comma-separated list of hostnames on which your app shall be available (e.g. `movieproxy.herokuapp.com`)
* `SECRET_KEY` – a Django secret key
* `TMDB_API_KEY` – a [TMDb API](https://developers.themoviedb.org/3/getting-started/introduction) key for fetching movie details

Optionally you can also add var `DEBUG` and set it to anything to anything to enable Django debug mode.

Then install the Heroku Postgres addon in the Resources tab. The app will automatically use this database.

Now deploy from the Deploy tab and wait for migrations to finish. After that, the app should be online and ready for use.


## Dependencies

Why these packages are in `requirements.txt`:

* `Django` – it's Django
* `requests` – for integration with the TMDb API
* `psycopg2` – for Postgres support
* `dj-database-url` – for Heroku Postgres add-on support
