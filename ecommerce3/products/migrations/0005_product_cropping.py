# Generated by Django 4.2.3 on 2023-07-17 09:44

from django.db import migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_remove_product_price_range_delete_pricefilter'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='cropping',
            field=image_cropping.fields.ImageRatioField('product_image', '200x200', adapt_rotation=False, allow_fullsize=False, free_crop=False, help_text=None, hide_image_field=False, size_warning=False, verbose_name='cropping'),
        ),
    ]
