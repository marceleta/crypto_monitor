from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AtivoViewSet

# Cria o roteador padrão
router = DefaultRouter()

# Registra o ViewSet 'Ativo' no roteador
router.register(r'ativos', AtivoViewSet, basename='ativo')

# Define as URLs
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
