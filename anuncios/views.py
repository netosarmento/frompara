from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator  # Importando Paginator
from .models import Categoria, Anuncio

def postagens(request, categoria_id=None):
    categorias = Categoria.objects.all()
    
    if categoria_id is not None:
        categoria = get_object_or_404(Categoria, id=categoria_id)
        anuncios_list = Anuncio.objects.filter(categoria=categoria).order_by('-criado_em')
    else:
        anuncios_list = Anuncio.objects.order_by('-criado_em')

    paginator = Paginator(anuncios_list, 6)  # 6 anúncios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categorias': categorias,
        'page_obj': page_obj,
    }
    return render(request, 'postagens.html', context)

def categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    categorias = Categoria.objects.all()
    anuncios = Anuncio.objects.filter(categoria=categoria)
    return render(request, 'postagens.html', {'categorias': categorias, 'anuncios': anuncios, 'categoria': categoria})

def anuncio(request, anuncio_id):
    anuncio_obj = get_object_or_404(Anuncio, id=anuncio_id)
    categorias = Categoria.objects.all()
    return render(request, 'anuncio.html', {'categorias': categorias, 'anuncio': anuncio_obj})

def search_view(request):
    query = request.GET.get('q')
    anuncios = Anuncio.objects.search(query) if query else Anuncio.objects.none()
    context = {
        'query': query,
        'anuncios': anuncios,
    }
    return render(request, 'search_results.html', context)
