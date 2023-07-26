# Generated by Django 4.2.3 on 2023-07-25 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0028_alter_orderitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('Return', 'Return'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Processing', 'Processing'), ('Pending', 'Pending'), ('Cancelled', 'Cancelled')], default='Pending', max_length=150),
        ),
    ]