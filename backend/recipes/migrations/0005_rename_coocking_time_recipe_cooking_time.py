# Generated by Django 3.2.3 on 2024-08-05 11:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_delete_follow'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='coocking_time',
            new_name='cooking_time',
        ),
    ]
