# Generated by Django 4.0.5 on 2022-06-21 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0010_transaction'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set(),
        ),
    ]
