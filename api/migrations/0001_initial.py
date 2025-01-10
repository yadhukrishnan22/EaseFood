# Generated by Django 5.1.4 on 2025-01-09 05:24

import django.contrib.auth.validators
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
            name='BaseModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='SellerCategory',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.basemodel')),
                ('seller_catname', models.CharField(max_length=200)),
            ],
            bases=('api.basemodel',),
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.basemodel')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('pin', models.CharField(blank=True, max_length=6, null=True, unique=True)),
                ('seller_category', models.CharField(choices=[('Hotel', 'Hotel'), ('Hospital Canteen', 'Hospital Canteen'), ('College Canteen', 'College Canteen')], default='Hotel', max_length=200)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('api.basemodel', models.Model),
        ),
        migrations.CreateModel(
            name='FoodCategory',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.basemodel')),
                ('food_category_name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('category_image', models.ImageField(null=True, upload_to='category_images')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=('api.basemodel',),
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.basemodel')),
                ('food_name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('food_image', models.ImageField(null=True, upload_to='food_images')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_available', models.BooleanField(default=True)),
                ('time_taken', models.PositiveIntegerField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('food_category_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.foodcategory')),
            ],
            bases=('api.basemodel',),
        ),
        migrations.CreateModel(
            name='SellerAccount',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.basemodel')),
                ('username', models.CharField(max_length=200)),
                ('bio', models.CharField(max_length=200, null=True)),
                ('profile_picture', models.ImageField(null=True, upload_to='profilepictures')),
                ('address', models.TextField(null=True)),
                ('phone_number', models.CharField(max_length=10)),
                ('description', models.TextField(null=True)),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            bases=('api.basemodel',),
        ),
        migrations.AddConstraint(
            model_name='foodcategory',
            constraint=models.UniqueConstraint(fields=('owner', 'food_category_name'), name='unique_category'),
        ),
        migrations.AddConstraint(
            model_name='food',
            constraint=models.UniqueConstraint(fields=('owner', 'food_name'), name='unique_food'),
        ),
    ]