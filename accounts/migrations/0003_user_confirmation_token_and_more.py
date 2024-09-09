# Generated by Django 5.0.4 on 2024-08-21 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='confirmation_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='confirmation_token_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='reset_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='reset_token_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
