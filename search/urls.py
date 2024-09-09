from django.urls import path
from .views import SearchProductView, SearchAnuncioView, SearchRedirectView

app_name = "search"

urlpatterns = [
    path('products/', SearchProductView.as_view(), name='search-products'),
    path('anuncios/', SearchAnuncioView.as_view(), name='search-anuncios'),
    path('', SearchRedirectView.as_view(), name='query'),
]
