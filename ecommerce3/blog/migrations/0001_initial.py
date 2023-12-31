# Generated by Django 4.2.3 on 2023-07-25 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blog_name', models.CharField(max_length=200, unique=True)),
                ('blog_image', models.ImageField(default='No image available', upload_to='photos/blog')),
                ('blog_discription', models.TextField(max_length=200)),
                ('slug', models.SlugField(max_length=250, unique=True)),
            ],
        ),
    ]
