# Generated by Django 2.2.16 on 2021-11-17 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='ddte_of_birth',
            new_name='date_of_birth',
        ),
    ]
