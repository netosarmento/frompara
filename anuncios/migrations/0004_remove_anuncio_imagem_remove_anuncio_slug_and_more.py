# Generated by Django 5.0.4 on 2024-06-29 12:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anuncios', '0003_anuncio_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='anuncio',
            name='imagem',
        ),
        migrations.RemoveField(
            model_name='anuncio',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='categoria',
            name='slug',
        ),
    ]
