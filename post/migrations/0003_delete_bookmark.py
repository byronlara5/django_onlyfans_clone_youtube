# Generated by Django 3.1.5 on 2021-01-28 04:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0002_bookmark'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Bookmark',
        ),
    ]
