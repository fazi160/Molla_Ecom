# Generated by Django 4.2.3 on 2023-07-12 07:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='price_range',
        ),
        migrations.DeleteModel(
            name='PriceFilter',
        ),
    ]
