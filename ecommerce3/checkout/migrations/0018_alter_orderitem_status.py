# Generated by Django 4.2.3 on 2023-07-21 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0017_alter_orderitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('Cancelled', 'Cancelled'), ('Return', 'Return'), ('Delivered', 'Delivered'), ('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Processing', 'Processing')], default='Pending', max_length=150),
        ),
    ]
