from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardViewSet, AtivoDetalheViewSet, PatrimonioEvolucaoViewSet

# Criar o router para registrar os ViewSets
router = DefaultRouter()

# Registrar o DashboardViewSet com a rota 'dashboard'
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

# Registrar outros ViewSets, se necessário
router.register(r'ativo-detalhe', AtivoDetalheViewSet, basename='ativo-detalhe')
router.register(r'patrimonio-evolucao', PatrimonioEvolucaoViewSet, basename='patrimonio-evolucao')

# Incluir as rotas geradas pelo router no urlpatterns
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
