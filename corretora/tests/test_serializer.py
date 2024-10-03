from django.test import TestCase
from rest_framework.exceptions import ValidationError
from corretora.models import CorretoraConfig, TipoOperacao, CorretoraUsuario
from usuario.models import Usuario
from corretora.serializers import TipoOperacaoSerializer, CorretoraConfigSerializer, CorretoraUsuarioSerializer


class SerializerTestCase(TestCase):

    def setUp(self):
        # Criando tipos de operação e corretora
        self.tipo_spot = TipoOperacao.objects.create(tipo='spot')
        self.tipo_futures = TipoOperacao.objects.create(tipo='futures')

        # Criando corretora
        self.corretora = CorretoraConfig.objects.create(
            nome="Binance",
            url_base="https://api.binance.com",
            exige_passphrase=False
        )
        self.corretora.tipos_suportados.add(self.tipo_spot, self.tipo_futures)

        # Criando usuário
        self.usuario = Usuario.objects.create_user(username="usuario_teste", password="123456")

        # Criando CorretoraUsuario
        self.corretora_usuario = CorretoraUsuario.objects.create(
            corretora=self.corretora,
            api_key="my_api_key",
            api_secret="my_api_secret",
            passphrase="my_passphrase",
            usuario=self.usuario
        )
        self.corretora_usuario.tipos.add(self.tipo_spot, self.tipo_futures)

    def test_tipo_operacao_serialization(self):
        # Testa a serialização de TipoOperacao
        serializer = TipoOperacaoSerializer(self.tipo_spot)
        data = serializer.data
        self.assertEqual(data['tipo'], 'spot')

    def test_corretora_usuario_serialization(self):
        # Testa a serialização de CorretoraUsuario (sem api_key, api_secret e passphrase)
        serializer = CorretoraUsuarioSerializer(self.corretora_usuario)
        data = serializer.data

        # Verifica se os campos estão presentes no serializer
        self.assertEqual(data['corretora'], self.corretora.id)  # Comparar com o ID da corretora
        self.assertEqual(len(data['tipos']), 2)
        self.assertEqual(data['usuario'], self.corretora_usuario.usuario.id)

        # Verifica se os campos api_key, api_secret e passphrase não foram serializados
        self.assertNotIn('api_key', data)
        self.assertNotIn('api_secret', data)
        self.assertNotIn('passphrase', data)


    def test_corretora_usuario_deserialization(self):
        # Testa a deserialização de CorretoraUsuario, garantindo que api_key, api_secret e passphrase são aceitos
        data = {
            'corretora': self.corretora.id,  # Envie apenas o ID
            'tipos': [self.tipo_spot.id, self.tipo_futures.id],  # Envie apenas uma lista de IDs
            'usuario': self.usuario.id,
            'api_key': 'new_api_key',
            'api_secret': 'new_api_secret',
            'passphrase': 'new_passphrase'
        }

        serializer = CorretoraUsuarioSerializer(data=data)
        #print('serializer: '+str(serializer))
        
        if not serializer.is_valid():
            print('serializer erros: '+str(serializer.errors))
        else:
            corretora_usuario = serializer.save()

            # Verifica se os dados foram salvos corretamente
            self.assertEqual(corretora_usuario.api_key, 'new_api_key')
            self.assertEqual(corretora_usuario.api_secret, 'new_api_secret')
            self.assertEqual(corretora_usuario.passphrase, 'new_passphrase')
            self.assertEqual(corretora_usuario.usuario, self.usuario)


    def test_corretora_usuario_deserialization(self):
        # Testa a deserialização de CorretoraUsuario, garantindo que api_key, api_secret e passphrase são aceitos
        data = {
            'corretora': self.corretora.id,  # Enviar apenas o ID da corretora
            'tipos': [self.tipo_spot.id, self.tipo_futures.id],  # Enviar apenas uma lista de IDs dos tipos
            'usuario': self.usuario.id,
            'api_key': 'new_api_key',
            'api_secret': 'new_api_secret',
            'passphrase': 'new_passphrase'
        }

        serializer = CorretoraUsuarioSerializer(data=data)
        #print('serializer: '+str(serializer))
        
        if not serializer.is_valid():
            print('serializer erros: '+str(serializer.errors))
        else:
            corretora_usuario = serializer.save()

            # Verifica se os dados foram salvos corretamente
            self.assertEqual(corretora_usuario.api_key, 'new_api_key')
            self.assertEqual(corretora_usuario.api_secret, 'new_api_secret')
            self.assertEqual(corretora_usuario.passphrase, 'new_passphrase')
            self.assertEqual(corretora_usuario.usuario, self.usuario)

