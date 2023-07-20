# Generated by Django 4.2.3 on 2023-07-20 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0013_alter_orderitem_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='od_status',
            field=models.CharField(default='Pending', max_length=255),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('Shipped', 'Shipped'), ('Return', 'Return'), ('Cancelled', 'Cancelled'), ('Delivered', 'Delivered'), ('Pending', 'Pending'), ('Processing', 'Processing')], default='Pending', max_length=150),
        ),
    ]
