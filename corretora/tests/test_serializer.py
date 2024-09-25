from django.test import TestCase
from usuario.models import Usuario
from corretora.models import Corretora
from corretora.serializers import CorretoraSerializer

class CorretoraSerializerTest(TestCase):

    def setUp(self):
        # Criando um usuário de teste
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )

        # Dados iniciais para a corretora
        self.corretora_data = {
            'nome': 'Test Corretora',
            'url_base': 'https://api.testcorretora.com',
            'api_key': 'test_api_key',
            'api_secret': 'test_api_secret',
            'passphrase': 'test_passphrase',
            'tipo': 'spot',
            'usuario': self.usuario
        }

    def test_serializer_valid_data(self):
        """Teste para validar se os dados do serializer são válidos"""
        serializer = CorretoraSerializer(data=self.corretora_data, context={'request': None})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['nome'], 'Test Corretora')

    def test_serializer_invalid_data(self):
        """Teste para validar se dados inválidos retornam erro"""
        invalid_data = self.corretora_data.copy()
        invalid_data['nome'] = ''  # Nome é obrigatório, então isso deve falhar
        serializer = CorretoraSerializer(data=invalid_data, context={'request': None})
        self.assertFalse(serializer.is_valid())
        self.assertIn('nome', serializer.errors)

    def test_serializer_create_corretora(self):
        """Teste para criação de corretora com o serializer"""
        serializer = CorretoraSerializer(data=self.corretora_data, context={'request': None})
        self.assertTrue(serializer.is_valid())
        corretora = serializer.save(usuario=self.usuario)
        self.assertEqual(corretora.nome, self.corretora_data['nome'])
        self.assertEqual(corretora.url_base, self.corretora_data['url_base'])
        self.assertEqual(corretora.usuario, self.usuario)

    def test_serializer_hidden_sensitive_fields(self):
        """Teste para garantir que os campos sensíveis não sejam expostos na serialização"""
        corretora = Corretora.objects.create(**self.corretora_data)
        serializer = CorretoraSerializer(corretora)
        self.assertNotIn('api_key', serializer.data)
        self.assertNotIn('api_secret', serializer.data)
        self.assertNotIn('passphrase', serializer.data)

    def test_serializer_update_corretora(self):
        """Teste para atualização de uma corretora com o serializer"""
        corretora = Corretora.objects.create(**self.corretora_data)
        updated_data = {
            'nome': 'Updated Corretora',
            'url_base': 'https://api.updatedcorretora.com',
            'tipo': 'futures'
        }
        serializer = CorretoraSerializer(instance=corretora, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        corretora = serializer.save()
        self.assertEqual(corretora.nome, 'Updated Corretora')
        self.assertEqual(corretora.url_base, 'https://api.updatedcorretora.com')
        self.assertEqual(corretora.tipo, 'futures')

