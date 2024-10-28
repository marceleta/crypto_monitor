from rest_framework import serializers
from .models import Ativo
from moeda.serializers import MoedaSerializer
from moeda.models import Moeda

class AtivoSerializer(serializers.ModelSerializer):
    # Usamos MoedaSerializer para o GET
    moeda = MoedaSerializer(read_only=True)
    # Usamos PrimaryKeyRelatedField para o UPDATE, apenas o ID
    moeda_id = serializers.PrimaryKeyRelatedField(queryset=Moeda.objects.all(), write_only=True)

    class Meta:
        model = Ativo
        fields = ['id', 'moeda', 'moeda_id', 'data_compra', 'valor_compra', 'usuario']
        read_only_fields = ['usuario']  # O usuário será associado automaticamente

    def update(self, instance, validated_data):
        # Aqui fazemos o update da moeda usando apenas o ID fornecido em moeda_id
        #print('AtivoSerializer update: '+str(instance.usuario))
        moeda = validated_data.pop('moeda_id')
        validated_data['moeda'] = moeda
        validated_data['usuario'] = instance.usuario
        return Ativo.objects.create(**validated_data)
    
    def create(self, validated_data):
        # Remove `moeda_id` do validated_data e associa o objeto `Moeda`
        moeda = validated_data.pop('moeda_id')
        ativo = Ativo.objects.create(moeda=moeda, **validated_data)
        return ativo
