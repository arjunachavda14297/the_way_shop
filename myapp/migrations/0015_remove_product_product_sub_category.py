# Generated by Django 4.1.3 on 2022-12-01 08:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0014_transaction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_sub_category',
        ),
    ]