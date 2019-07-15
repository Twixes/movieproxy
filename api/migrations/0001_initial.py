# Generated by Django 2.2.3 on 2019-07-09 09:08

import requests
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            'Genre',
            [
                ('id', models.PositiveIntegerField(primary_key=True)),
                ('name', models.CharField(max_length=1000))
            ]
        ),
        migrations.CreateModel(
            'Movie',
            [
                ('id', models.PositiveIntegerField(primary_key=True)),
                ('poster_path', models.CharField(max_length=1000, null=True)),
                ('adult', models.BooleanField()),
                ('overview', models.TextField()),
                ('release_date', models.DateField()),
                ('genres', models.ManyToManyField(related_name='movies', to='api.Genre')),
                ('original_title', models.CharField(max_length=1000)),
                ('original_language', models.CharField(max_length=1000)),
                ('title', models.CharField(max_length=1000)),
                ('backdrop_path', models.CharField(max_length=1000, null=True)),
                ('popularity', models.FloatField()),
                ('vote_count', models.PositiveIntegerField()),
                ('video', models.BooleanField()),
                ('vote_average', models.FloatField())
            ]
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('movie', models.ForeignKey(on_delete=models.deletion.CASCADE, to='api.Movie'))
            ]
        )
    ]
