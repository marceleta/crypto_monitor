from rest_framework import serializers
from corretora.models import CorretoraConfig, TipoOperacao, CorretoraUsuario


class TipoOperacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoOperacao
        fields = ['id', 'tipo']


class CorretoraConfigSerializer(serializers.ModelSerializer):
    tipos_suportados = TipoOperacaoSerializer(many=True, read_only=True)

    class Meta:
        model = CorretoraConfig
        fields = ['id', 'nome', 'url_base', 'exige_passphrase', 'tipos_suportados', 'logo']

    def get_logo(self, obj):
        request = self.context.get('request')
        if obj.logo:
            return request.build_absolute_uri(obj.logo.url)
        return None


class CorretoraUsuarioSerializer(serializers.ModelSerializer):
    
    corretora = serializers.PrimaryKeyRelatedField(queryset=CorretoraConfig.objects.all())
    tipos = serializers.PrimaryKeyRelatedField(many=True, queryset=TipoOperacao.objects.all())

    # Definimos os campos de API como write_only para que eles não sejam expostos no frontend
    api_key = serializers.CharField(write_only=True)
    api_secret = serializers.CharField(write_only=True)
    passphrase = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = CorretoraUsuario
        fields = ['id', 'corretora', 'tipos', 'usuario', 'api_key', 'api_secret', 'passphrase']

    def create(self, validated_data):
        # Extrai os dados de tipos (usando apenas IDs)
        tipos_data = validated_data.pop('tipos')
        #print('tipos_data: '+str(tipos_data))

        # Cria a instância do CorretoraUsuario com os dados validados
        corretora_usuario = CorretoraUsuario.objects.create(**validated_data)

        # Lida com os tipos de operação (ManyToManyField)
        corretora_usuario.tipos.set(tipos_data)  # Usamos .set() para atribuir os tipos por ID

        return corretora_usuario

    def update(self, instance, validated_data):
        # Atualiza apenas os campos específicos que foram enviados
        instance.api_key = validated_data.get('api_key', instance.api_key)
        instance.api_secret = validated_data.get('api_secret', instance.api_secret)
        instance.passphrase = validated_data.get('passphrase', instance.passphrase)
        
        # Atualiza os tipos de operação (ManyToManyField) usando apenas IDs
        if 'tipos' in validated_data:
            tipos_data = validated_data.pop('tipos')
            instance.tipos.set(tipos_data)  # Usamos .set() para substituir os tipos

        instance.save()
        return instance
    
class CorretoraUsuarioDetailSerializer(serializers.ModelSerializer):
    # Inclui os detalhes da corretora com todos os campos relevantes
    corretora = CorretoraConfigSerializer(read_only=True)
    tipos = TipoOperacaoSerializer(many=True, read_only=True)

    class Meta:
        model = CorretoraUsuario
        fields = ['id', 'tipos', 'usuario', 'corretora']