# Generated by Django 3.2.5 on 2022-02-07 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookclubs', '0003_alter_user_dob'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1),
        ),
    ]