# Generated by Django 5.0.4 on 2024-08-29 00:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_confirmation_token_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='guestemail',
            old_name='active',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='active',
            new_name='is_active',
        ),
    ]
