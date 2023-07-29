# Generated by Django 4.2.3 on 2023-07-28 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0030_alter_orderitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('Return', 'Return'), ('Pending', 'Pending'), ('Delivered', 'Delivered'), ('Shipped', 'Shipped'), ('Cancelled', 'Cancelled'), ('Processing', 'Processing')], default='Pending', max_length=150),
        ),
    ]
