# Generated by Django 4.2.16 on 2025-02-04 08:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_vote_negative_ballot'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='election',
            name='decrypted_total',
        ),
    ]
