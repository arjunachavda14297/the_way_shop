# Generated by Django 4.1.3 on 2022-12-24 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0018_rename_product_price_order_grand_total_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='order_status',
            field=models.BooleanField(default=False),
        ),
    ]
