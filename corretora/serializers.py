from rest_framework import serializers
from .models import Corretora

class CorretoraSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(write_only=True, required=False)
    api_secret = serializers.CharField(write_only=True, required=False)
    passphrase = serializers.CharField(write_only=True, required=False)
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Corretora
        fields = [
            'id',
            'nome',
            'url_base',
            'tipo',
            'usuario',
            'logo',
            'api_key',
            'api_secret',
            'passphrase',
        ]
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True},
            'passphrase': {'write_only': True},
            'usuario': {'read_only': True},
        }

    def create(self, validated_data):
        # Verifique se o usuário foi passado explicitamente ou via request
        usuario = validated_data.pop('usuario', None) or self.context.get('request').user
        if not usuario:
            raise serializers.ValidationError("Usuário não autenticado.")
        
        validated_data['usuario'] = usuario
        return super().create(validated_data)




