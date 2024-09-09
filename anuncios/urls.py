from django.urls import path
from .views import categoria, anuncio, postagens, search_view

urlpatterns = [
    path('postagens/', postagens, name='postagens'),
    path('categoria/<int:categoria_id>/', postagens, name='categoria'),
    path('anuncio/<int:anuncio_id>/', anuncio, name='anuncio'),  
    path('search/', search_view, name='search'),
    # outras URLs
]
