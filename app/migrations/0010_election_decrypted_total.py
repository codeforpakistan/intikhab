# Generated by Django 4.2.16 on 2025-02-04 10:24

from django.db import migrations
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_merge_20250204_1022'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='decrypted_total',
            field=encrypted_model_fields.fields.EncryptedCharField(default='', editable=False),
        ),
    ]
