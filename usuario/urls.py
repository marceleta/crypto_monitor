from django.urls import path
from .views import UserProfileView

urlpatterns = [
    path('api/v1/profile/', UserProfileView.as_view(), name='profile'),
]
