from decimal import Decimal
from django.test import TestCase
from usuario.models import Usuario
from moeda.models import Moeda, HistoricoCotacao

class MoedaCRUDTests(TestCase):

    def setUp(self):
        # Cria um usuário para testar a associação de moedas
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        # Cria uma moeda para testes
        self.moeda = Moeda.objects.create(
            nome="Bitcoin",
            token="BTC",
            cor="#F7931A",
            logo=None,
            usuario=self.usuario  # Associando a moeda ao usuário
        )

    def test_create_moeda(self):
        # Teste para criação de uma nova moeda diretamente no modelo
        nova_moeda = Moeda.objects.create(
            nome="Ethereum",
            token="ETH",
            cor="#3C3C3D",
            logo=None,
            usuario=self.usuario
        )
        #print('count: '+str(Moeda.objects.count()))
        self.assertEqual(Moeda.objects.count(), 2)
        self.assertEqual(nova_moeda.nome, "Ethereum")
        self.assertEqual(nova_moeda.token, "ETH")
        self.assertEqual(nova_moeda.usuario, self.usuario)

    def test_read_moeda(self):
        # Teste para leitura da moeda criada no setUp
        moeda = Moeda.objects.get(token="BTC")
        self.assertEqual(moeda.nome, "Bitcoin")
        self.assertEqual(moeda.usuario, self.usuario)

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
        # Cria um usuário para associar à moeda, se necessário
        self.usuario = Usuario.objects.create_user(username='testuser', password='12345')

        # Criando uma moeda para ser usada nos testes e associando o usuário, se aplicável
        self.moeda = Moeda.objects.create(nome='Bitcoin', token='BTC', logo='btc_logo.png', usuario=self.usuario)


    def test_create_historico_cotacao(self):
        # Teste de criação de uma cotação
        cotacao = HistoricoCotacao.objects.create(moeda=self.moeda, preco=50000.1234567890)
        self.assertEqual(HistoricoCotacao.objects.count(), 1)
        self.assertEqual(cotacao.moeda.nome, 'Bitcoin')
        self.assertEqual(cotacao.preco, 50000.1234567890)

    def test_read_historico_cotacao(self):
        # Teste de leitura de uma cotação
        cotacao = HistoricoCotacao.objects.create(moeda=self.moeda, preco=50000.1234567890)
        recuperada = HistoricoCotacao.objects.get(id=cotacao.id)
        self.assertEqual(recuperada.moeda.nome, 'Bitcoin')
        self.assertEqual(recuperada.preco, Decimal('50000.1234567890'))

    def test_update_historico_cotacao(self):
        # Teste de atualização de uma cotação
        cotacao = HistoricoCotacao.objects.create(moeda=self.moeda, preco=50000.1234567890)
        cotacao.preco = 51000.9876543210
        cotacao.save()
        recuperada = HistoricoCotacao.objects.get(id=cotacao.id)
        self.assertEqual(recuperada.preco, Decimal('51000.9876543210'))

    def test_delete_historico_cotacao(self):
        # Teste de exclusão de uma cotação
        cotacao = HistoricoCotacao.objects.create(moeda=self.moeda, preco=50000.1234567890)
        cotacao.delete()
        self.assertEqual(HistoricoCotacao.objects.count(), 0)

    def test_unique_together(self):
        # Teste da restrição de unicidade (unique_together) para uma cotação por dia
        HistoricoCotacao.objects.create(moeda=self.moeda, preco=50000.1234567890)
        
        # Tentativa de criar outra cotação para a mesma moeda e data
        with self.assertRaises(Exception):
            HistoricoCotacao.objects.create(moeda=self.moeda, preco=51000.9876543210)

