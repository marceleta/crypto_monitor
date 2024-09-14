from django.test import TestCase
from usuario.models import Usuario
from moeda.models import Moeda

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
