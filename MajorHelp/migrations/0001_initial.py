# Generated by Django 5.1.3 on 2025-04-04 20:28

import MajorHelp.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='DiscussionCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FinancialAid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('location', models.CharField(max_length=256)),
                ('amount', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='DiscussionThread',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_pinned', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='threads', to='MajorHelp.discussioncategory')),
            ],
        ),
        migrations.CreateModel(
            name='Major',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('major_name', models.CharField(max_length=255)),
                ('major_description', models.TextField(blank=True)),
                ('slug', models.SlugField(editable=False, unique=True)),
                ('department', models.CharField(choices=[('Humanities and Social Sciences', 'Humanities and Social Sciences'), ('Natural Sciences and Mathematics', 'Natural Sciences and Mathematics'), ('Business and Economics', 'Business and Economics'), ('Education', 'Education'), ('Engineering and Technology', 'Engineering and Technology'), ('Health Sciences', 'Health Sciences'), ('Arts and Design', 'Arts and Design'), ('Agriculture and Environmental Studies', 'Agriculture and Environmental Studies'), ('Communication and Media', 'Communication and Media'), ('Law and Criminal Justice', 'Law and Criminal Justice')], max_length=50)),
                ('in_state_min_tuition', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('in_state_max_tuition', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('out_of_state_min_tuition', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('out_of_state_max_tuition', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('fees', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('grad_in_state_min_tuition', models.IntegerField(default=0, help_text='Minimum in-state tuition for graduate students.', validators=[django.core.validators.MinValueValidator(0)])),
                ('grad_in_state_max_tuition', models.IntegerField(default=0, help_text='Maximum in-state tuition for graduate students.', validators=[django.core.validators.MinValueValidator(0)])),
                ('grad_out_of_state_min_tuition', models.IntegerField(default=0, help_text='Minimum out-of-state tuition for graduate students.', validators=[django.core.validators.MinValueValidator(0)])),
                ('grad_out_of_state_max_tuition', models.IntegerField(default=0, help_text='Maximum out-of-state tuition for graduate students.', validators=[django.core.validators.MinValueValidator(0)])),
                ('courses', models.ManyToManyField(blank=True, related_name='majors', to='MajorHelp.course')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='major',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='major_courses', to='MajorHelp.major'),
        ),
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('location', models.CharField(default='', max_length=255)),
                ('is_public', models.BooleanField(default=True, help_text='Check if the university is public; leave unchecked for private')),
                ('aboutText', models.TextField(default='')),
                ('TotalUndergradStudents', models.IntegerField(default=0)),
                ('TotalGradStudents', models.IntegerField(default=0)),
                ('GraduationRate', models.DecimalField(decimal_places=1, default=0.0, max_digits=4)),
                ('primary_color', models.CharField(default='#268f95', max_length=7)),
                ('secondary_color', models.CharField(default='#FFFFFF', max_length=7)),
                ('in_state_base_min_tuition', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('in_state_base_max_tuition', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('out_of_state_base_min_tuition', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('out_of_state_base_max_tuition', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('fees', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('slug', models.SlugField(default='', editable=False, unique=True)),
                ('applicableAids', models.ManyToManyField(blank=True, related_name='university', to='MajorHelp.financialaid')),
            ],
        ),
        migrations.AddField(
            model_name='major',
            name='university',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='majors', to='MajorHelp.university'),
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('prospective_student', 'Prospective Student'), ('current_student', 'Current Student'), ('alumni', 'Alumni'), ('university_staff', 'University Staff'), ('admin', 'Admin')], default='prospective_student', max_length=20)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('savedCalcs', models.JSONField(default=dict)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UniversityRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_text', models.TextField()),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ThreadReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='MajorHelp.discussionthread')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MajorReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_text', models.TextField(max_length=500)),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
                ('rating', models.DecimalField(decimal_places=1, default=0, max_digits=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('major', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='major_reviews', to='MajorHelp.major')),
                ('university', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='MajorHelp.university')),
                ('user', models.ForeignKey(default=MajorHelp.models.get_default_user, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('major', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='MajorHelp.major')),
                ('university', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='MajorHelp.university')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='discussionthread',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.CharField(max_length=50)),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UniversityReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('review_text', models.CharField(max_length=500)),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='university_review', to='MajorHelp.university')),
            ],
            options={
                'unique_together': {('username', 'university')},
            },
        ),
        migrations.CreateModel(
            name='UniversityRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('campus', 'Campus'), ('athletics', 'Athletics'), ('safety', 'Safety'), ('social', 'Social'), ('professor', 'Professor'), ('dorm', 'Dorm'), ('dining', 'Dining')], max_length=20)),
                ('rating', models.DecimalField(decimal_places=1, max_digits=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='MajorHelp.university')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='university_ratings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('university', 'category', 'user')},
            },
        ),
    ]
