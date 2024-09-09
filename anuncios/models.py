from django.db import models
from django.db.models import Q

class AnuncioQuerySet(models.query.QuerySet):
    def search(self, query):
        lookups = (Q(titulo__icontains=query) |
                   Q(descricao__icontains=query) |
                   Q(categoria__titulo__icontains=query))
        return self.filter(lookups).distinct()

class AnuncioManager(models.Manager):
    def get_queryset(self):
        return AnuncioQuerySet(self.model, using=self._db)

    def search(self, query):
        return self.get_queryset().search(query)

class Categoria(models.Model):
    titulo = models.CharField(max_length=40)

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['titulo']

class Anuncio(models.Model):
    titulo = models.CharField(max_length=40)
    imagem = models.ImageField(upload_to='static/img/')
    descricao = models.TextField(null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)
    alterado_em = models.DateTimeField(auto_now=True)

    objects = AnuncioManager()

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['-id']
