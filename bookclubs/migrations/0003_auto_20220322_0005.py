# Generated by Django 3.2.5 on 2022-03-22 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookclubs', '0002_auto_20220321_1943'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meeting',
            name='time_end',
        ),
        migrations.AddField(
            model_name='meeting',
            name='duration',
            field=models.IntegerField(default=30),
        ),
    ]
