from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.contrib.auth.views import LogoutView 
from django.urls import path, include
from django.views.generic import TemplateView
from carts.views import cart_home, cart_detail_api_view
from django.contrib.auth import views as auth_views
from accounts.views import LoginView, RegisterView, LogoutView, ConfirmEmailView, guest_register_view
from addresses.views import checkout_address_create_view, checkout_address_reuse_view
from .views import (home_page,  
                    about_page, 
                    contact_page,
                    faq,
                    quemsomos,
                    termos,
                    politicas,
                    SAC,
                    fotos,
)

urlpatterns = [
    path('', home_page, name='home'),
    path('about/', about_page, name='about'),
    path('contact/', contact_page, name='contact'),
    path('cart/', include("carts.urls", namespace="cart")),
    path('anuncios/', include('anuncios.urls')),#adicioando a urls, dos anuncios
    path('carts/', include('carts.urls')),
    path('checkout/address/create/', checkout_address_create_view, name='checkout_address_create'),
    path('checkout/address/reuse/', checkout_address_reuse_view, name='checkout_address_reuse'),
    path('api/cart/', cart_detail_api_view, name='api-cart'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/guest/', guest_register_view, name='guest_register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile-created/', TemplateView.as_view(template_name='accounts/profile_created.html'), name='profile_created'),
    path('bootstrap/', TemplateView.as_view(template_name='bootstrap/example.html')),
    path('search/', include("search.urls", namespace="search")),
    path('products/', include("products.urls", namespace="products")),
    path('admin/', admin.site.urls),
    path('faq/', faq, name='faq'),
    path('quemsomos/', quemsomos, name='quemsomos'),
    path('termos/', termos, name='termos'),
    path('politicas/', politicas, name='politicas'),
    path('SAC/', SAC, name='SAC'),
    path('fotografia/', fotos, name='fotografia'),
    path('confirm-email/<uidb64>/<token>/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]
