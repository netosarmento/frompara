from django.shortcuts import render, redirect
from django.views.generic import ListView, View
from django.http import HttpResponseRedirect
from products.models import Product
from anuncios.models import Anuncio

class SearchProductView(ListView):
    template_name = "search/view.html"
    context_object_name = 'products'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        query = request.GET.get('q', None)
        if query is not None:
            return Product.objects.search(query)
        return Product.objects.none()

class SearchAnuncioView(ListView):
    template_name = "search/view.html"
    context_object_name = 'anuncios'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        query = request.GET.get('q', None)
        if query is not None:
            return Anuncio.objects.search(query)
        return Anuncio.objects.none()

class SearchRedirectView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        search_type = request.GET.get('type', 'products')
        if search_type == 'anuncios':
            return HttpResponseRedirect(f'/search/anuncios/?q={query}')
        return HttpResponseRedirect(f'/search/products/?q={query}')
