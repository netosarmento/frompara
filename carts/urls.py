
from django.urls import path
from .views import (
    cart_home,
    checkout_home,
    cart_update,
    payment_successful,
    payment_cancelled,
    stripe_webhook,
    
    
)

app_name = 'carts'

urlpatterns = [
    path('', cart_home, name='home'),
    path('checkout/', checkout_home, name='checkout'),
    path('payment_successful/', payment_successful, name='payment_successful'),
    path('payment_cancelled/', payment_cancelled, name='payment_cancelled'),
    path('stripe-webhook/', stripe_webhook, name='stripe_webhook'),
    path('update/', cart_update, name='update'),
]
