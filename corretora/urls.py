from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TipoOperacaoViewSet, CorretoraConfigViewSet, CorretoraUsuarioViewSet, CorretoraUsuarioDetailViewSet

# Cria o roteador padrão
router = DefaultRouter()

# Registra as rotas para os ViewSets
router.register(r'tipos-operacao', TipoOperacaoViewSet, basename='tipos-operacao')
router.register(r'corretoras', CorretoraConfigViewSet, basename='corretoras')
router.register(r'corretoras-usuario', CorretoraUsuarioViewSet, basename='corretora-usuario')
router.register(r'corretoras-usuario-detalhes', CorretoraUsuarioDetailViewSet, basename='corretora-usuario-detalhes')

# Inclui as rotas no padrão de URLs
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
