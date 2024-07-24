from django.contrib.auth import authenticate, get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from anuncios.models import Anuncio, Categoria


from .forms import ContactForm

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def home_page(request):
    categorias = Categoria.objects.all()
    ultimos_anuncios = Anuncio.objects.all()[:6]
    if request.user.is_authenticated:
        context['premium_content'] = 'Você é um usuário Premium'
    return render(request, 'home_page.html', {'categorias': categorias,
                                         'anuncios': ultimos_anuncios})

    
def about_page(request):
    context = {
                    "title": "Página Sobre",
                    "content": "Bem vindo a FromPara, onde divulgamos todas as belezas e historias do Para."
              }
    return render(request, "about/view.html", context)

def contact_page(request):
    contact_form = ContactForm(request.POST or None)
    context = {
                    "title": "Página de Contatos Oficial.",
                    "content": "Bem vindo a página de contato FromPara, aqui deixe seu contato, para dar pedir informaçoes, dar sugestões ou se busca parcerias.",
                    "form": contact_form	
              }
    if contact_form.is_valid():
        print(contact_form.cleaned_data)
        if is_ajax(request):
            return JsonResponse({"message": "Obrigado!"})
    if contact_form.errors:
        errors = contact_form.errors.as_json()
        if is_ajax(request):
            return HttpResponse(errors, status=400, content_type='application/json')
    return render(request, "contact/view.html", context)

def categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)

    categorias = Categoria.objects.all()

    anuncios = Anuncio.objects.filter(categoria=categoria)

    return render(request, 'postagens.html', {'categorias': categorias,
                                         'anuncios': anuncios,
                                         'categoria': categoria})


def anuncio(request, anuncio_id):
    anuncio = get_object_or_404(Anuncio, id=anuncio_id)

    categorias = Categoria.objects.all()
    ultimos_anuncios = Anuncio.objects.all()[:2]

    return render(request, 'anuncio.html', {'categorias': categorias,
                                         'anuncio': anuncio, 'anuncios': ultimos_anuncios})
    

def faq(request):
    
    return render(request, 'faq.html')

def quemsomos(request):
    
    return render(request, 'quemsomos.html')


def politicas(request):
    
    return render(request, 'politicas.html')

def termos(request):
    
    return render(request, 'termos.html')