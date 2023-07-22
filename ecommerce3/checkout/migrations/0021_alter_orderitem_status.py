# Generated by Django 4.2.3 on 2023-07-22 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0020_alter_orderitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('Processing', 'Processing'), ('Return', 'Return'), ('Pending', 'Pending'), ('Delivered', 'Delivered'), ('Shipped', 'Shipped'), ('Cancelled', 'Cancelled')], default='Pending', max_length=150),
        ),
    ]