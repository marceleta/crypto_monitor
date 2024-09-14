from rest_framework import serializers
from .models import Ativo

class AtivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ativo
        fields = ['id', 'moeda', 'data_compra', 'valor_compra', 'usuario']
        read_only_fields = ['usuario']  # O usuário será associado automaticamente
