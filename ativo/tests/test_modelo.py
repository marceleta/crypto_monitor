from django.test import TestCase
from ativo.models import Ativo
from moeda.models import Moeda
from usuario.models import Usuario

class AtivoModelTests(TestCase):

    def setUp(self):
        # Cria um usuário para os testes
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        # Cria uma moeda para associar ao ativo
        self.moeda = Moeda.objects.create(
            nome="Bitcoin",
            token="BTC",
            cor="#F7931A",
            logo=None,
            usuario=self.usuario
        )

        # Cria um ativo inicial para os testes
        self.ativo = Ativo.objects.create(
            moeda=self.moeda,
            data_compra="2024-09-12",
            valor_compra=10000.00,
            usuario=self.usuario
        )

    def test_create_ativo(self):
        # Teste para criação de um novo ativo diretamente no modelo
        novo_ativo = Ativo.objects.create(
            moeda=self.moeda,
            data_compra="2024-09-11",
            valor_compra=5000.00,
            usuario=self.usuario
        )
        self.assertEqual(Ativo.objects.count(), 2)  # Deve haver 2 ativos agora
        self.assertEqual(novo_ativo.moeda, self.moeda)
        self.assertEqual(novo_ativo.valor_compra, 5000.00)

    def test_read_ativo(self):
        # Teste para leitura de um ativo existente
        ativo = Ativo.objects.get(id=self.ativo.id)
        self.assertEqual(ativo.moeda, self.moeda)
        self.assertEqual(ativo.valor_compra, 10000.00)
        self.assertEqual(str(ativo.data_compra), "2024-09-12")

    def test_update_ativo(self):
        # Teste para atualizar um ativo existente
        self.ativo.valor_compra = 12000.00
        self.ativo.save()

        # Recarregar o ativo do banco de dados para verificar a atualização
        ativo_atualizado = Ativo.objects.get(id=self.ativo.id)
        self.assertEqual(ativo_atualizado.valor_compra, 12000.00)

    def test_delete_ativo(self):
        # Teste para deletar um ativo
        self.ativo.delete()
        self.assertEqual(Ativo.objects.count(), 0)  # Deve haver 0 ativos agora
