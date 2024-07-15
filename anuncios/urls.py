from django.urls import path
from .views import categoria, anuncio, postagens

urlpatterns = [
    path('postagens/', postagens, name='postagens'),
    path('categoria/<int:categoria_id>/', categoria, name='categoria'),
    path('anuncio/<int:anuncio_id>/', anuncio, name='anuncio'),  
]