from rest_framework import serializers
from .models import Moeda

class MoedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moeda
        fields = ['id', 'nome', 'token', 'cor', 'logo', 'usuario']
        read_only_fields = ['usuario']
