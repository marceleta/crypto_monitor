from django.test import TestCase
from corretora.models import CorretoraConfig, TipoOperacao, CorretoraUsuario
from usuario.models import Usuario

class CorretoraConfigTestCase(TestCase):
    def setUp(self):
        self.tipo_spot = TipoOperacao.objects.create(tipo='spot')
        self.tipo_futures = TipoOperacao.objects.create(tipo='futures')

    def test_create_corretora(self):
        # Testa a criação de uma corretora
        corretora = CorretoraConfig.objects.create(
            nome="Bybit",
            url_base="https://api.bybit.com",
            exige_passphrase=True,
        )
        corretora.tipos_suportados.add(self.tipo_spot, self.tipo_futures)
        corretora.save()

        self.assertEqual(corretora.nome, "Bybit")
        self.assertEqual(corretora.url_base, "https://api.bybit.com")
        self.assertTrue(corretora.exige_passphrase)
        self.assertIn(self.tipo_spot, corretora.tipos_suportados.all())
        self.assertIn(self.tipo_futures, corretora.tipos_suportados.all())

    def test_logo_upload(self):
        # Testa o upload do logo
        corretora = CorretoraConfig.objects.create(
            nome="Binance",
            url_base="https://api.binance.com",
            exige_passphrase=False,
            logo="logos_corretoras/binance.png"
        )
        self.assertEqual(corretora.logo, "logos_corretoras/binance.png")


class CorretoraUsuarioTestCase(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(username="usuario_teste", password="123456")
        self.tipo_spot = TipoOperacao.objects.create(tipo='spot')
        self.tipo_futures = TipoOperacao.objects.create(tipo='futures')

        self.corretora = CorretoraConfig.objects.create(
            nome="Coinbase",
            url_base="https://api.coinbase.com",
            exige_passphrase=True,
        )
        self.corretora.tipos_suportados.add(self.tipo_spot, self.tipo_futures)
        self.corretora.save()

        self.corretora_usuario = CorretoraUsuario.objects.create(
            corretora=self.corretora,
            api_key="test_api_key",
            api_secret="test_api_secret",
            passphrase="test_passphrase",
            usuario=self.usuario
        )
        self.corretora_usuario.tipos.add(self.tipo_spot, self.tipo_futures)
        self.corretora_usuario.save()

    def test_create_corretora_usuario(self):
        # Testa a criação de um CorretoraUsuario
        self.assertEqual(self.corretora_usuario.api_key, "test_api_key")
        self.assertEqual(self.corretora_usuario.api_secret, "test_api_secret")
        self.assertEqual(self.corretora_usuario.passphrase, "test_passphrase")
        self.assertIn(self.tipo_spot, self.corretora_usuario.tipos.all())
        self.assertIn(self.tipo_futures, self.corretora_usuario.tipos.all())
        self.assertEqual(self.corretora_usuario.usuario, self.usuario)

    def test_update_corretora_usuario(self):
        # Atualiza os dados de um CorretoraUsuario
        self.corretora_usuario.api_key = "updated_api_key"
        self.corretora_usuario.api_secret = "updated_api_secret"
        self.corretora_usuario.passphrase = "updated_passphrase"
        self.corretora_usuario.save()

        # Recarrega o objeto do banco de dados para garantir que as mudanças foram salvas
        updated_corretora_usuario = CorretoraUsuario.objects.get(id=self.corretora_usuario.id)

        # Verifica se os dados foram atualizados corretamente
        self.assertEqual(updated_corretora_usuario.api_key, "updated_api_key")
        self.assertEqual(updated_corretora_usuario.api_secret, "updated_api_secret")
        self.assertEqual(updated_corretora_usuario.passphrase, "updated_passphrase")


