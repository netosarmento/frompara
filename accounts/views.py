from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, FormView, View
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from .signals import user_logged_in
from .forms import LoginForm, RegisterForm, GuestForm
from .models import GuestEmail, User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

# Função para gerar um token de confirmação por e-mail
def generate_confirmation_token(user):
    from django.core.signing import Signer
    signer = Signer()
    return signer.sign_object(user.pk)

# Função para verificar o token de confirmação por e-mail
def verify_confirmation_token(token):
    from django.core.signing import Signer
    signer = Signer()
    try:
        user_id = signer.unsign_object(token)
        return user_id
    except Exception:
        return None

# Função para enviar o e-mail de confirmação com o link do token
def send_confirmation_email(user, request):
    token = generate_confirmation_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = request.get_host()  # Usa o domínio dinâmico da solicitação
    subject = 'Confirmação de Cadastro'
    context = {
        'user': user,
        'domain': domain,
        'uid': uid,
        'token': token
    }
    html_message = render_to_string('accounts/confirmation_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    # Envio do e-mail
    send_mail(
        subject,
        plain_message,
        from_email,
        [to_email],
        html_message=html_message,
        fail_silently=False
    )

# Função para enviar o e-mail de redefinição de senha
def send_password_reset_email(user, request):
    token = user.reset_token
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = request.get_host()
    subject = 'Redefinição de Senha'
    context = {
        'user': user,
        'domain': domain,
        'uid': uid,
        'token': token
    }
    html_message = render_to_string('accounts/password_reset_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    # Envio do e-mail
    send_mail(
        subject,
        plain_message,
        from_email,
        [to_email],
        html_message=html_message,
        fail_silently=False
    )

class LoginView(FormView):
    form_class = LoginForm
    success_url = '/'  # Redireciona para a raiz do projeto
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(request=self.request, username=email, password=password)

        if user is not None:
            # Limpar tentativas de login falhadas
            cache.set(f'login_attempts_{email}', 0, timeout=0)  # Remove as tentativas falhadas do cache
            login(self.request, user)
            user_logged_in.send(sender=user.__class__, instance=user, request=self.request)
            try:
                del self.request.session['guest_email_id']
            except KeyError:
                pass
            return super(LoginView, self).form_valid(form)
        else:
            # Incrementar tentativas de login falhadas
            attempts = cache.get(f'login_attempts_{email}', 0)
            attempts += 1
            cache.set(f'login_attempts_{email}', attempts, timeout=3600)  # 1 hora para o bloqueio

            # Verificar se o usuário está bloqueado
            if attempts >= 3:
                block_time = cache.get(f'block_time_{email}')
                if block_time and timezone.now() < block_time:
                    form.add_error(None, "Too many failed login attempts. Please try again later.")
                    return self.form_invalid(form)
                else:
                    # Reiniciar o contador de tentativas após o bloqueio
                    cache.set(f'block_time_{email}', timezone.now() + timedelta(minutes=5), timeout=3600)
                    form.add_error(None, "Too many failed login attempts. Please try again in 5 minutes.")
                    return self.form_invalid(form)

            form.add_error(None, "Invalid login senha errada.")
            return self.form_invalid(form)

class LogoutView(View):
    template_name = 'accounts/logout.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            "content": "Você efetuou o logout com sucesso! :)"
        }
        logout(request)
        return render(request, self.template_name, context)

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/profile-created/'  # Atualizado para redirecionar após o registro bem-sucedido

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        user.set_confirmation_token()
        send_confirmation_email(user, self.request)
        return response
    
    def form_invalid(self, form):
        # Se o formulário for inválido, ele será redirecionado de volta ao template com erros
        return super().form_invalid(form)

class ConfirmEmailView(View):
    def get(self, request, uidb64, token):
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
        
        if user.confirmation_token == token and user.is_confirmation_token_valid():
            user.active = True
            user.confirmation_token = ''
            user.confirmation_token_expires_at = None
            user.save()
            return redirect('/login/')
        else:
            return render(request, 'accounts/confirmation_invalid.html')

class PasswordResetRequestView(FormView):
    form_class = RegisterForm
    template_name = 'accounts/password_reset_request.html'

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        user = get_object_or_404(User, email=email)
        user.set_reset_token()
        send_password_reset_email(user, self.request)
        return redirect('/password-reset/done/')

class PasswordResetConfirmView(View):
    def get(self, request, uidb64, token):
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)

        if user.reset_token == token and user.is_reset_token_valid():
            # Render password reset form
            context = {'uid': uid, 'token': token}
            return render(request, 'accounts/password_reset_form.html', context)
        else:
            return render(request, 'accounts/password_reset_invalid.html')

    def post(self, request, uidb64, token):
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
        
        if user.reset_token == token and user.is_reset_token_valid():
            password = request.POST.get('password')
            user.set_password(password)
            user.reset_token = ''
            user.reset_token_expires_at = None
            user.save()
            return redirect('/login/')
        else:
            return render(request, 'accounts/password_reset_invalid.html')

def guest_register_view(request):
    form = GuestForm(request.POST or None)
    context = {
        "form": form
    }
    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        email = form.cleaned_data.get("email")
        new_guest_email = GuestEmail.objects.create(email=email)
        request.session['guest_email_id'] = new_guest_email.id
        if redirect_path:
            return redirect(redirect_path)
        else:
            return redirect("/register/")
    return render(request, 'accounts/guest_register.html', context)
