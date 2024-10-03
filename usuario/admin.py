from django.contrib import admin
from .models import Usuario

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')  # Campos que aparecerão na lista de usuários
    search_fields = ('email', 'first_name', 'last_name')  # Campos de busca
    list_filter = ('is_active', 'is_staff')  # Filtros no lado direito
    ordering = ('email',)  # Ordem dos itens

# Registra o modelo Usuario com as personalizações no admin
admin.site.register(Usuario, UsuarioAdmin)

