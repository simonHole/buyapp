# Generated by Django 4.0.4 on 2022-06-10 11:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_rename_facebook_profile_site'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='username',
            new_name='nickname',
        ),
    ]