# Generated by Django 4.2.3 on 2023-07-17 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_product_product_image_crop'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_image_crop',
        ),
    ]
