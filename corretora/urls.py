from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CorretoraViewSet

router = DefaultRouter()
router.register(r'corretoras', CorretoraViewSet, basename='corretora')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
