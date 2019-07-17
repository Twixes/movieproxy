# MovieProxy

A simple Django REST API.

## Running with Heroku

This is the easiest way to run MovieProxy.
Create a Heroku app, connect this repository to it and, in the Settings tab, add the following config vars to it:

* DISABLE_COLLECTSTATIC – set this to '1' to disable a Heroku feature that would be problematic in this case
* ALLOWED_HOSTS – a comma-separated list of hostnames on which your app shall be available (e.g. movieproxy.herokuapp.com)
* SECRET_KEY – a Django secret key
* TMDB_API_KEY – a [TMDb API](https://developers.themoviedb.org/3/getting-started/introduction) key for fetching movie details

Then install the Heroku Postgres addon in the Resources tab. The app will automatically use this database.

Now deploy from the Deploy tab and wait for migrations to finish. After that, the app should be online and ready for use.
