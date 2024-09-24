from rest_framework import serializers
from .models import BybitCorretora

class BybitCorretoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = BybitCorretora
        fields = ['id', 'nome']  # Excluímos os campos 'api_key' e 'api_secret'
