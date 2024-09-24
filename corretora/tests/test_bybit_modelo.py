from django.test import TestCase
from corretora.models import BybitCorretora
from usuario.models import Usuario


class BybitCorretoraCRUDTest(TestCase):

    

    def setUp(self):
        # Criação de um usuário para associar à corretora
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        # Configuração inicial de uma corretora
        self.corretora = BybitCorretora.objects.create(
            nome="Bybit",
            api_key="api_key_123",
            api_secret="api_secret_123",
            usuario=self.usuario
        )

    def test_create_corretora(self):
        # Teste de criação de uma corretora
        BybitCorretora.objects.create(
            nome="Binance",
            api_key="binance_api_key",
            api_secret="binance_api_secret"
        )
        self.assertEqual(BybitCorretora.objects.count(), 2)

    def test_read_corretora(self):
        # Teste de leitura de uma corretora
        corretora = BybitCorretora.objects.get(nome="Bybit")
        self.assertEqual(corretora.nome, "Bybit")
        self.assertEqual(corretora.api_key, "api_key_123")
        self.assertEqual(corretora.api_secret, "api_secret_123")

    def test_update_corretora(self):
        # Teste de atualização dos dados de uma corretora
        self.corretora.nome = "Bybit Atualizado"
        self.corretora.api_key = "nova_api_key"
        self.corretora.save()

        corretora_atualizada = BybitCorretora.objects.get(id=self.corretora.id)
        self.assertEqual(corretora_atualizada.nome, "Bybit Atualizado")
        self.assertEqual(corretora_atualizada.api_key, "nova_api_key")

    def test_delete_corretora(self):
        # Teste de exclusão de uma corretora
        corretora_id = self.corretora.id
        self.corretora.delete()
        
        with self.assertRaises(BybitCorretora.DoesNotExist):
            BybitCorretora.objects.get(id=corretora_id)

        self.assertEqual(BybitCorretora.objects.count(), 0)
