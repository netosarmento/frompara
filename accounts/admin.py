# accounts/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import GuestEmail

# Obtenha o modelo de usuário personalizado
User = get_user_model()

class UserAdmin(BaseUserAdmin):
    # Formulários para adicionar e alterar instâncias de usuário
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # Campos exibidos na lista de usuários
    list_display = ['email', 'admin', 'is_active']  # Corrigido para is_active
    list_filter = ['admin', 'staff', 'is_active']  # Corrigido para is_active

    # Conjunto de campos exibidos na página de detalhes do usuário
    fieldsets = (
        (None, {'fields': ('full_name', 'email', 'password')}),
        ('Permissions', {'fields': ('admin', 'staff', 'is_active')}),  # Corrigido para is_active
    )

    # Campos exibidos ao adicionar um novo usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password_2')}
        ),
    )

    search_fields = ['email', 'full_name']
    ordering = ['email']
    filter_horizontal = ()

# Registre o modelo User com o UserAdmin personalizado
admin.site.register(User, UserAdmin)

# Remova o modelo Group da administração, se não estiver usando
admin.site.unregister(Group)

class GuestEmailAdmin(admin.ModelAdmin):
    search_fields = ['email']
    list_display = ['email', 'is_active', 'timestamp']  # Corrigido para is_active
    list_filter = ['is_active']  # Corrigido para is_active

# Registre o modelo GuestEmail com o GuestEmailAdmin
admin.site.register(GuestEmail, GuestEmailAdmin)
