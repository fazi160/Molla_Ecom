# Generated by Django 4.2.3 on 2023-07-12 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0003_alter_orderitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('Processing', 'Processing'), ('Return', 'Return'), ('Delivered', 'Delivered'), ('Shipped', 'Shipped'), ('Cancelled', 'Cancelled'), ('Pending', 'Pending')], default='Pending', max_length=150),
        ),
    ]
