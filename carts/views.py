from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from accounts.forms import LoginForm, GuestForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from accounts.models import GuestEmail
from addresses.forms import AddressForm
from addresses.models import Address
from billing.models import BillingProfile
from orders.models import Order
from products.models import Product
from .models import Cart
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from payment.models import UserPayment, GuestPayment
from e_commerce import settings
from django.urls import reverse
import stripe, time

stripe.api_key = settings.STRIPE_SECRET_KEY

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = [{
        "id": x.id,
        "url": x.get_absolute_url(), 
        "name": x.title, 
        "price": x.price
        } for x in cart_obj.products.all()]
    # products_list = []
    # for x in cart_obj.products.all():
    #     products_list.append({
    #         {"name": x.title, "price": x.price}
    #     })
    cart_data = {"products": products, "subtotal": cart_obj.subtotal, "total": cart_obj.total}
    return JsonResponse(cart_data)

def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    return render(request, "carts/home.html", {"cart": cart_obj})

def cart_update(request):
    product_id = request.POST.get('product_id')
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Mostrar mensagem ao usuário, esse produto acabou!")
            return redirect("cart:home")
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
            added = False
        else:
            cart_obj.products.add(product_obj) # cart_obj.products.add(product_id)
            added = True
        request.session['cart_items'] = cart_obj.products.count()
        # return redirect(product_obj.get_absolute_url())
        if is_ajax(request):
            print("Ajax request")
            json_data = {
                "added": added,
                "removed": not added,
                "cartItemCount": cart_obj.products.count()
            }
            return JsonResponse(json_data)
            #return JsonResponse({"message": "Erro 400"}, status = 400)
    return redirect("cart:home")

@login_required
def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None

    if cart_created or cart_obj.products.count() == 0:
        return redirect("cart:home")

    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()
    billing_address_id = request.session.get("billing_address_id", None)
    shipping_address_id = request.session.get("shipping_address_id", None)
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None

    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session["billing_address_id"]
        if billing_address_id or shipping_address_id:
            order_obj.save()

    if request.method == "POST":
        if order_obj is None:
            return HttpResponse(status=400)  # Retorna erro se order_obj não estiver definido

        # Captura a escolha de entrega do usuário
        delivery_option = request.POST.get('delivery_option', 'no')

        # Ajusta o total com base na escolha de entrega
        if delivery_option == 'yes':
            order_obj.shipping_total = order_obj.shipping_total  # Mantém o custo de entrega
        else:
            order_obj.shipping_total = 0.00  # Zera o custo de entrega

        order_obj.save()  # Salve o pedido após a atualização

        # Continue com o processo de checkout
        is_done = order_obj.check_done()
        if is_done:
            line_items = [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product.title,
                        },
                        'unit_amount': int(product.price * 100),
                    },
                    'quantity': 1,
                } for product in cart_obj.products.all()
            ]

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri(reverse('carts:payment_successful')) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(reverse('carts:payment_cancelled')),
            )

            if request.user.is_authenticated:
                user_payment, created = UserPayment.objects.get_or_create(
                    user=request.user,
                    defaults={'stripe_checkout_id': checkout_session.id}
                )
                if not created:
                    user_payment.stripe_checkout_id = checkout_session.id
                    user_payment.save()
            else:
                guest_email, _ = GuestEmail.objects.get_or_create(email=billing_profile.email)
                guest_payment, created = GuestPayment.objects.get_or_create(
                    guest_email=guest_email,
                    defaults={'stripe_checkout_id': checkout_session.id}
                )
                if not created:
                    guest_payment.stripe_checkout_id = checkout_session.id
                    guest_payment.save()

            return redirect(checkout_session.url, code=303)

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs": address_qs,
    }
    return render(request, "carts/checkout.html", context)



def payment_successful(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session_id = request.GET.get('session_id', None)

    try:
        # Tenta recuperar a sessão de checkout
        session = stripe.checkout.Session.retrieve(checkout_session_id)
    except stripe.error.InvalidRequestError as e:
        # Captura erros relacionados a requisições inválidas
        return render(request, 'carts/payment_error.html', {'error': str(e)})

    try:
        # Tenta recuperar o cliente associado à sessão
        customer = stripe.Customer.retrieve(session.customer)
    except stripe.error.InvalidRequestError as e:
        # Captura erros ao recuperar o cliente
        return render(request, 'carts/payment_error.html', {'error': str(e)})

    user_id = request.user.user_id

    try:
        # Tenta obter o registro de pagamento do usuário
        user_payment = UserPayment.objects.get(accounts=user_id)
        user_payment.stripe_checkout_id = checkout_session_id
        user_payment.payment_bool = True
        user_payment.save()
    except UserPayment.DoesNotExist:
        # Captura o caso em que o registro de pagamento não existe
        return render(request, 'carts/payment_cancelled.html')

    return render(request, 'carts/payment_successful.html', {'customer': customer})


def payment_cancelled(request):
	return render(request, 'carts/payment_cancelled.html')


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    time.sleep(10)
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # O segredo do seu webhook

    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Process the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id', None)
        time.sleep(15)
        # Encontre o UserPayment correspondente
        user_payment = UserPayment.objects.filter(stripe_checkout_id=session_id).first()
        if user_payment:
            user_payment.payment_bool = True  # Atualiza o status do pagamento
            user_payment.save()

            # Enviar e-mail com o recibo
            subject = "Confirmação de Pagamento"
            message = render_to_string('carts/payment_confirmation_email.html', {
                'user': user_payment.user,
                'session': session,
                'total': session.amount_total / 100,  # Valor em dólares
            })
            recipient_list = [user_payment.user.email]  # E-mail do usuário
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)

    return HttpResponse(status=200)





