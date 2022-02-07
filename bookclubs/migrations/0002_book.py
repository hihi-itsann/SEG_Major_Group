# Generated by Django 3.2.5 on 2022-02-07 16:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookclubs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ISBN', models.CharField(max_length=10, unique=True, validators=[django.core.validators.MinLengthValidator(10)])),
                ('title', models.CharField(max_length=100, unique=True)),
                ('author', models.CharField(max_length=100)),
                ('year_of_publication', models.CharField(max_length=4, validators=[django.core.validators.RegexValidator(message='Year should be digit number', regex='^(?=.*[0-9]).*$')])),
                ('publisher', models.CharField(max_length=100)),
                ('image_url_s', models.URLField()),
                ('image_url_m', models.URLField()),
                ('image_url_l', models.URLField()),
            ],
        ),
    ]
