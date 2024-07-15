from django.contrib import admin

# Register your models here.
from anuncios import models

admin.site.register(models.Categoria)
admin.site.register(models.Anuncio)