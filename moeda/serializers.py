from rest_framework import serializers
from .models import Moeda, HistoricoCotacao
from corretora.models import CorretoraUsuario

class MoedaSerializer(serializers.ModelSerializer):
    corretora = serializers.PrimaryKeyRelatedField(queryset=CorretoraUsuario.objects.all(), allow_null=True)

    class Meta:
        model = Moeda
        fields = ['id', 'nome', 'token', 'cor', 'logo', 'usuario', 'corretora']

class HistoricoCotacaoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = HistoricoCotacao
        fields = ['moeda', 'data', 'preco']  # Campos que serão serializados
        
        # Se quiser que 'data' seja apenas leitura (por ser auto-gerada), pode adicionar:
        read_only_fields = ['data']

