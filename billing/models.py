from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User, GuestEmail
import stripe, environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()
stripe.api_key = env('STRIPE_PUBLIC_KEY')

User = settings.AUTH_USER_MODEL

class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        if user.is_authenticated:
            obj, created = self.model.objects.get_or_create(
                user=user, email=user.email
            )
        elif guest_email_id is not None:
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(
                email=guest_email_obj.email
            )
        return obj, created

class BillingProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    customer_id = models.CharField(max_length=120, null=True, blank=True)
    objects = BillingProfileManager()

    def __str__(self):
        return self.email

@receiver(post_save, sender=BillingProfile)
def billing_profile_created_receiver(sender, instance, created, **kwargs):
    if created and not instance.customer_id and instance.email:
        try:
            customer = stripe.Customer.create(email=instance.email)
            instance.customer_id = customer.id
            instance.save()
        except stripe.error.StripeError as e:
            print(f"Stripe API error: {e}")
        except Exception as e:
            print(f"Error creating customer: {e}")

@receiver(post_save, sender=User)
def user_created_receiver(sender, instance, created, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)
