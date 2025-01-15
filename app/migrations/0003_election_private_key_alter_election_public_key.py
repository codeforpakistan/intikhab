# Generated by Django 4.2.16 on 2025-01-15 07:23

from django.db import migrations
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_election_public_key_vote_encrypted_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='private_key',
            field=encrypted_model_fields.fields.EncryptedCharField(default=''),
        ),
        migrations.AlterField(
            model_name='election',
            name='public_key',
            field=encrypted_model_fields.fields.EncryptedCharField(default=''),
        ),
    ]
