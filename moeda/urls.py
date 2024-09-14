from django.urls import path, include
from rest_framework.routers import DefaultRouter
from moeda.views import MoedaViewSet

router = DefaultRouter()
router.register(r'moedas', MoedaViewSet, basename='moeda')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
