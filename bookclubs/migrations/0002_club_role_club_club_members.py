# Generated by Django 4.0.2 on 2022-02-06 10:10

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookclubs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('club_name', models.CharField(max_length=20, unique=True, validators=[django.core.validators.RegexValidator(message='Club name must consist of at least four alphanumericals in first word', regex='^\\w{4,}.*$')])),
                ('location', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=520)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('club_role', models.CharField(choices=[('APP', 'Applicant'), ('MEM', 'Member'), ('OFF', 'Officer'), ('MOD', 'Moderator'), ('OWN', 'Owner'), ('BAN', 'BannedMember')], default='APP', max_length=3)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookclubs.club')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='club',
            name='club_members',
            field=models.ManyToManyField(through='bookclubs.Role', to=settings.AUTH_USER_MODEL),
        ),
    ]
