# Generated by Django 4.2.16 on 2025-01-28 08:42

from django.db import migrations
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_merge_20250127_0625'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='negative_ballot',
            field=encrypted_model_fields.fields.EncryptedCharField(default='', editable=False),
        ),
    ]
