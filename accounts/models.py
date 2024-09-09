# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta
import secrets  # Import necessário para gerar tokens


class UserManager(BaseUserManager):
    def create_user(self, email, full_name=None, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError("O Usuário deve ter um endereço de email!")
        if not password:
            raise ValueError("O Usuário deve ter uma senha!")
        
        # Normaliza o email
        email = self.normalize_email(email)
        
        # Cria o objeto do usuário
        user_obj = self.model(
            full_name=full_name,
            email=email,
            is_active=is_active,  # Usando is_active corretamente
            staff=is_staff,
            admin=is_admin
        )
        
        user_obj.set_password(password)  # Muda a senha
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, full_name=None, password=None):
        return self.create_user(
            email,
            full_name,
            password=password,
            is_staff=True
        )

    def create_superuser(self, email, full_name=None, password=None):
        return self.create_user(
            email,
            full_name=full_name,
            password=password,
            is_staff=True,
            is_admin=True
        )

class User(AbstractBaseUser):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)  # Pode fazer login
    staff = models.BooleanField(default=False)  # Usuário do staff, não superusuário
    admin = models.BooleanField(default=False)  # Superusuário
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Novos campos para confirmação e redefinição de senha
    confirmation_token = models.CharField(max_length=255, blank=True, null=True)
    confirmation_token_expires_at = models.DateTimeField(blank=True, null=True)
    reset_token = models.CharField(max_length=255, blank=True, null=True)
    reset_token_expires_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name if self.full_name else self.email

    def get_short_name(self):
        return self.email

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    def set_confirmation_token(self):
        from django.core.signing import Signer
        signer = Signer()
        self.confirmation_token = signer.sign_object(self.pk)
        self.confirmation_token_expires_at = timezone.now() + timedelta(hours=1)
        self.save()

    def is_confirmation_token_valid(self):
        from django.core.signing import Signer
        if self.confirmation_token_expires_at >= timezone.now():
            signer = Signer()
            try:
                signer.unsign_object(self.confirmation_token)
                return True
            except Exception:
                return False
        return False

    def set_reset_token(self):
        from django.core.signing import Signer
        signer = Signer()
        self.reset_token = signer.sign_object(self.pk)
        self.reset_token_expires_at = timezone.now() + timedelta(hours=1)
        self.save()

    def is_reset_token_valid(self):
        from django.core.signing import Signer
        if self.reset_token_expires_at >= timezone.now():
            signer = Signer()
            try:
                signer.unsign_object(self.reset_token)
                return True
            except Exception:
                return False
        return False

class GuestEmail(models.Model):
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
