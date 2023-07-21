# Generated by Django 4.2.3 on 2023-07-17 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_product_cropping'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='cropping',
        ),
        migrations.AlterField(
            model_name='product',
            name='product_image',
            field=models.ImageField(upload_to='product_images/'),
        ),
    ]