from decimal import Decimal
from django.test import TestCase
from usuario.models import Usuario
from moeda.models import Moeda, HistoricoCotacao
from django.contrib.contenttypes.models import ContentType
from corretora.models import CorretoraUsuario, CorretoraConfig

class MoedaCRUDTests(TestCase):

    def setUp(self):
        # Cria um usuário para testar a associação de moedas
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        # Cria uma configuração de corretora
        self.corretora_config = CorretoraConfig.objects.create(
            nome="Bybit",
            url_base="https://api.bybit.com",
            exige_passphrase=False
        )

        # Cria uma associação de corretora com o usuário
        self.bybit_corretora = CorretoraUsuario.objects.create(
            corretora=self.corretora_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            usuario=self.usuario
        )

        # Cria uma moeda para testes
        self.moeda = Moeda.objects.create(
            nome="Bitcoin",
            token="BTC",
            cor="#F7931A",
            logo=None,
            usuario=self.usuario,
            corretora=self.bybit_corretora
        )

    def test_create_moeda(self):
        # Teste para criação de uma nova moeda com corretora
        nova_moeda = Moeda.objects.create(
            nome="Ethereum",
            token="ETH",
            cor="#3C3C3D",
            logo=None,
            usuario=self.usuario,
            corretora=self.bybit_corretora
        )
        self.assertEqual(Moeda.objects.count(), 2)
        self.assertEqual(nova_moeda.nome, "Ethereum")
        self.assertEqual(nova_moeda.token, "ETH")
        self.assertEqual(nova_moeda.usuario, self.usuario)
        self.assertEqual(nova_moeda.corretora, self.bybit_corretora)

    def test_read_moeda(self):
        # Teste para leitura da moeda criada no setUp
        moeda = Moeda.objects.get(token="BTC")
        self.assertEqual(moeda.nome, "Bitcoin")
        self.assertEqual(moeda.usuario, self.usuario)
        self.assertEqual(moeda.corretora, self.bybit_corretora)

    def test_update_moeda(self):
        # Teste para atualizar a moeda criada no setUp
        self.moeda.nome = "Bitcoin Atualizado"
        self.moeda.save()
        moeda_atualizada = Moeda.objects.get(token="BTC")
        self.assertEqual(moeda_atualizada.nome, "Bitcoin Atualizado")

    def test_delete_moeda(self):
        # Teste para excluir a moeda criada no setUp
        moeda = Moeda.objects.get(token="BTC")
        moeda.delete()
        self.assertEqual(Moeda.objects.count(), 0)


class HistoricoCotacaoTests(TestCase):
    
    def setUp(self):
        # Cria um usuário para associar à moeda
        self.usuario = Usuario.objects.create_user(username='testuser', password='12345')

        # Cria uma configuração de corretora necessária para a CorretoraUsuario
        self.corretora_config = CorretoraConfig.objects.create(
            nome="Bybit",
            url_base="https://api.bybit.com",
            exige_passphrase=False
        )

        # Cria uma CorretoraUsuario associada ao usuário
        self.corretora_usuario = CorretoraUsuario.objects.create(
            corretora=self.corretora_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            usuario=self.usuario
        )

        # Obtém o ContentType da CorretoraUsuario
        self.corretora_content_type = ContentType.objects.get_for_model(CorretoraUsuario)

        # Cria uma moeda associada ao usuário e à corretora
        self.moeda = Moeda.objects.create(
            nome='Bitcoin',
            token='BTC',
            logo='btc_logo.png',
            usuario=self.usuario,
            corretora_content_type=self.corretora_content_type,
            corretora_object_id=self.corretora_usuario.id
        )

    def test_create_historico_cotacao(self):
         # Teste de criação de uma cotação
        cotacao = HistoricoCotacao.objects.create(
            moeda=self.moeda,
            data='2024-09-12',
            abertura=Decimal('50000.123456789'),
            fechamento=Decimal('51000.987654321'),
            alta=Decimal('52000.543210987'),
            baixa=Decimal('49000.654321098'),
            volume=Decimal('100.123456789')
        )
        self.assertEqual(HistoricoCotacao.objects.count(), 1)
        self.assertEqual(cotacao.moeda.nome, 'Bitcoin')
        self.assertEqual(cotacao.abertura, Decimal('50000.123456789'))
        self.assertEqual(cotacao.fechamento, Decimal('51000.987654321'))
        self.assertEqual(cotacao.alta, Decimal('52000.543210987'))
        self.assertEqual(cotacao.baixa, Decimal('49000.654321098'))
        self.assertEqual(cotacao.volume, Decimal('100.123456789'))

    def test_read_historico_cotacao(self):
        # Teste de leitura de uma cotação
        cotacao = HistoricoCotacao.objects.create(
            moeda=self.moeda,
            data="2024-09-12",
            abertura=50000.1234567890,
            fechamento=50500.9876543210,
            alta=51000.1234567890,
            baixa=49500.6543210987,
            volume=100.5678901234
        )
        recuperada = HistoricoCotacao.objects.get(id=cotacao.id)
        self.assertEqual(recuperada.moeda.nome, 'Bitcoin')
        self.assertEqual(recuperada.abertura, Decimal('50000.123456789'))
        self.assertEqual(recuperada.fechamento, Decimal('50500.9876543210'))
        self.assertEqual(recuperada.alta, Decimal('51000.1234567890'))
        self.assertEqual(recuperada.baixa, Decimal('49500.6543210987'))
        self.assertEqual(recuperada.volume, Decimal('100.5678901234'))

    def test_update_historico_cotacao(self):
        # Teste de atualização de uma cotação
        cotacao = HistoricoCotacao.objects.create(
            moeda=self.moeda,
            data="2024-09-12",
            abertura=50000.1234567890,
            fechamento=50500.9876543210,
            alta=51000.1234567890,
            baixa=49500.6543210987,
            volume=100.5678901234
        )
        cotacao.fechamento = 51000.1234567890
        cotacao.save()
        recuperada = HistoricoCotacao.objects.get(id=cotacao.id)
        self.assertEqual(recuperada.fechamento, Decimal('51000.1234567890'))

    def test_delete_historico_cotacao(self):
        # Teste de exclusão de uma cotação
        cotacao = HistoricoCotacao.objects.create(
            moeda=self.moeda,
            data="2024-09-12",
            abertura=50000.1234567890,
            fechamento=50500.9876543210,
            alta=51000.1234567890,
            baixa=49500.6543210987,
            volume=100.5678901234
        )
        cotacao.delete()
        self.assertEqual(HistoricoCotacao.objects.count(), 0)



