# Generated by Django 3.2.5 on 2022-02-07 16:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookclubs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='dob',
            field=models.DateField(default=datetime.date(2022, 2, 7)),
        ),
    ]
