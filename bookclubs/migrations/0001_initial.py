# Generated by Django 3.2.5 on 2022-04-08 01:38

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('userID', models.IntegerField(null=True, unique=True)),
                ('username', models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(message='Username must consist of @ followed by at least three alphanumerics', regex='^@\\w{3,}$')])),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('bio', models.CharField(blank=True, max_length=520)),
                ('dob', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('location', models.CharField(blank=True, max_length=50)),
                ('city', models.CharField(blank=True, max_length=50)),
                ('country', models.CharField(blank=True, max_length=50)),
                ('meeting_preference', models.CharField(blank=True, choices=[('O', 'Online'), ('P', 'In-person')], max_length=1)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('ISBN', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.MinLengthValidator(10)])),
                ('title', models.CharField(max_length=100, unique=True)),
                ('author', models.CharField(max_length=100)),
                ('year_of_publication', models.IntegerField(validators=[django.core.validators.MinValueValidator(1000), django.core.validators.MaxValueValidator(2022)])),
                ('publisher', models.CharField(max_length=100)),
                ('image_url_s', models.URLField()),
                ('image_url_m', models.URLField()),
                ('image_url_l', models.URLField()),
                ('genre', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('club_name', models.CharField(max_length=20, unique=True, validators=[django.core.validators.RegexValidator(message='Club name must consist of at least four alphanumerics in first word', regex='^\\w{4,}.*$')])),
                ('meeting_status', models.CharField(choices=[('ONL', 'Online'), ('OFF', 'In-person')], default='OFF', max_length=3)),
                ('location', models.CharField(max_length=256)),
                ('city', models.CharField(blank=True, max_length=256)),
                ('country', models.CharField(blank=True, max_length=256)),
                ('public_status', models.CharField(choices=[('PUB', 'Public'), ('PRI', 'Private')], default='PRI', max_length=3)),
                ('genre', models.CharField(default='Fiction', max_length=256)),
                ('description', models.CharField(max_length=520)),
            ],
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(default='', max_length=120)),
                ('description', models.TextField(blank=True, max_length=520)),
                ('meeting_status', models.CharField(choices=[('ONL', 'Online'), ('OFF', 'In-person')], default='OFF', max_length=3)),
                ('location', models.CharField(blank=True, max_length=120)),
                ('date', models.DateField()),
                ('time_start', models.TimeField()),
                ('duration', models.IntegerField(default=30)),
                ('join_link', models.URLField(blank=True, null=True)),
                ('start_link', models.URLField(blank=True, null=True)),
                ('book', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bookclubs.book')),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meeting_club', to='bookclubs.club')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('body', models.CharField(max_length=520)),
                ('post_date', models.DateField(auto_now_add=True)),
                ('post_datetime', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookclubs.club')),
            ],
            options={
                'ordering': ['-post_date', '-post_datetime'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('club_role', models.CharField(choices=[('MEM', 'Member'), ('MOD', 'Moderator'), ('OWN', 'Owner'), ('BAN', 'Banned')], default='MEM', max_length=3)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookclubs.club')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'club')},
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.CharField(max_length=520)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('related_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='bookclubs.post')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ClubBookAverageRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.FloatField(default=0)),
                ('number_of_ratings', models.IntegerField()),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookclubs.book')),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookclubs.club')),
            ],
        ),
        migrations.AddField(
            model_name='club',
            name='club_members',
            field=models.ManyToManyField(through='bookclubs.Role', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='BookStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('U', 'Unread'), ('R', 'Reading'), ('F', 'Finished')], default='U', max_length=1)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookclubs.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BookRatingReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(10.0)])),
                ('review', models.CharField(blank=True, max_length=520)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookclubs.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote_type', models.BooleanField()),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_vote', to='bookclubs.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_vote', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'post')},
            },
        ),
        migrations.CreateModel(
            name='MeetingAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting_role', models.CharField(choices=[('H', 'Host'), ('A', 'Attendee')], max_length=1)),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookclubs.meeting')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'meeting')},
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statement', models.CharField(max_length=520)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Accepted'), ('R', 'Rejected')], max_length=1)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookclubs.club')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('user', 'club')},
            },
        ),
    ]
