#create your models
# payment/models.py
from django.db import models
from django.conf import settings
from accounts.models import User, GuestEmail
from django.dispatch import receiver
from django.db.models.signals import post_save
import stripe

User = settings.AUTH_USER_MODEL

stripe.api_key = settings.STRIPE_SECRET_KEY

class UserPayment(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE) #corrigindo o erro
    payment_bool = models.BooleanField(default=False)
    stripe_checkout_id =models.CharField(max_length=500)
    
class GuestPayment(models.Model):
    guest_email = models.OneToOneField(GuestEmail, on_delete=models.CASCADE)
    payment_bool = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500)

    def __str__(self):
        return self.guest_email.email


class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    stripe_checkout_id = models.CharField(max_length=500)

@receiver(post_save, sender=User)
def create_user_receiver(sender, instance, created, **kwargs):
    if created:
        UserPayment.objects.create(User=instance)
    
