# Generated by Django 4.1.3 on 2022-12-31 14:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0020_adress'),
    ]

    operations = [
        migrations.RenameField(
            model_name='adress',
            old_name='ads',
            new_name='address',
        ),
    ]
