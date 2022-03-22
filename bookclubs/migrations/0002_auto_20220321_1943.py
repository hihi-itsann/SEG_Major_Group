# Generated by Django 3.2.5 on 2022-03-21 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookclubs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='join_link',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='meeting',
            name='start_link',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='date',
            field=models.DateField(),
        ),
    ]