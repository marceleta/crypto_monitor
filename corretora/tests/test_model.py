# tests/test_models.py

from django.test import TestCase
from corretora.models import Corretora
from usuario.models import Usuario

class CorretoraModelTest(TestCase):

    def setUp(self):
        # Criação de um usuário para associar à corretora
        self.usuario = Usuario.objects.create(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        # Dados padrão para uma corretora
        self.corretora_data = {
            'nome': 'Test Corretora',
            'url_base': 'https://api.testcorretora.com',
            'api_key': 'test_api_key',
            'api_secret': 'test_api_secret',
            'passphrase': 'test_passphrase',
            'tipo': 'spot',
            'usuario': self.usuario
        }
        self.corretora = Corretora.objects.create(**self.corretora_data)

    def test_create_corretora(self):
        """Teste para criação de uma corretora"""
        self.assertEqual(Corretora.objects.count(), 1)
        self.assertEqual(self.corretora.nome, 'Test Corretora')
        self.assertEqual(self.corretora.usuario, self.usuario)

    def test_read_corretora(self):
        """Teste para leitura de uma corretora"""
        corretora = Corretora.objects.get(id=self.corretora.id)
        self.assertEqual(corretora.nome, 'Test Corretora')

    def test_update_corretora(self):
        """Teste para atualização de uma corretora"""
        self.corretora.nome = 'Updated Corretora'
        self.corretora.save()
        updated_corretora = Corretora.objects.get(id=self.corretora.id)
        self.assertEqual(updated_corretora.nome, 'Updated Corretora')

    def test_delete_corretora(self):
        """Teste para deleção de uma corretora"""
        self.corretora.delete()
        self.assertEqual(Corretora.objects.count(), 0)
