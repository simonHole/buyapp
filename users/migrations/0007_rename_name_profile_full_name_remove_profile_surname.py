# Generated by Django 4.0.5 on 2022-06-21 01:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_profile_surname'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='name',
            new_name='full_name',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='surname',
        ),
    ]
