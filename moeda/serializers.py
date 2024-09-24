from rest_framework import serializers
from .models import Moeda, HistoricoCotacao

class MoedaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Moeda
        fields = ['id', 'nome', 'token', 'cor', 'logo', 'usuario', 'corretora']

class HistoricoCotacaoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = HistoricoCotacao
        fields = ['moeda', 'data', 'preco']  # Campos que serão serializados
        
        # Se quiser que 'data' seja apenas leitura (por ser auto-gerada), pode adicionar:
        read_only_fields = ['data']

