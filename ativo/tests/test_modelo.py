from django.test import TestCase
from ativo.models import Ativo
from moeda.models import Moeda
from usuario.models import Usuario
from corretora.models import CorretoraConfig, CorretoraUsuario, TipoOperacao
from ativo.signals import iniciar_busca_apos_criacao_ativo
from django.db.models.signals import post_save

class AtivoModelTests(TestCase):

    def setUp(self):

        post_save.disconnect(iniciar_busca_apos_criacao_ativo, sender=Ativo)

        # Cria um usuário para os testes
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        # Cria uma configuração de corretora
        self.corretora_config = CorretoraConfig.objects.create(
            nome="Bybit",
            url_base="https://api.bybit.com",
            exige_passphrase=False
        )

        # Cria um tipo de operação
        self.tipo_operacao = TipoOperacao.objects.create(tipo='spot')

        # Cria uma associação de corretora com o usuário
        self.corretora_usuario = CorretoraUsuario.objects.create(
            corretora=self.corretora_config,
            api_key="fake_api_key",
            api_secret="fake_api_secret",
            usuario=self.usuario
        )
        self.corretora_usuario.tipos.add(self.tipo_operacao)

        # Cria uma moeda para associar ao ativo
        self.moeda = Moeda.objects.create(
            nome="Bitcoin",
            token="BTC",
            cor="#F7931A",
            logo=None,
            usuario=self.usuario,
            corretora=self.corretora_usuario  # Associando a corretora ao campo GenericForeignKey
        )

        # Cria um ativo inicial para os testes
        self.ativo = Ativo.objects.create(
            moeda=self.moeda,
            data_compra="2024-09-12",
            quantidade=0.5,  # Adicionando o campo quantidade
            valor_compra=10000.00,
            usuario=self.usuario
        )

    def test_create_ativo(self):
        # Teste para criação de um novo ativo diretamente no modelo
        novo_ativo = Ativo.objects.create(
            moeda=self.moeda,
            data_compra="2024-09-11",
            quantidade=1.0,  # Adicionando a quantidade no novo ativo
            valor_compra=5000.00,
            usuario=self.usuario
        )
        self.assertEqual(Ativo.objects.count(), 2)  # Deve haver 2 ativos agora
        self.assertEqual(novo_ativo.moeda, self.moeda)
        self.assertEqual(novo_ativo.valor_compra, 5000.00)
        self.assertEqual(novo_ativo.quantidade, 1.0)  # Verifica a quantidade

    def test_read_ativo(self):
        # Teste para leitura de um ativo existente
        ativo = Ativo.objects.get(id=self.ativo.id)
        self.assertEqual(ativo.moeda, self.moeda)
        self.assertEqual(ativo.valor_compra, 10000.00)
        self.assertEqual(ativo.quantidade, 0.5)  # Verifica a quantidade lida
        self.assertEqual(str(ativo.data_compra), "2024-09-12")

    def test_update_ativo(self):
        # Teste para atualizar um ativo existente
        self.ativo.valor_compra = 12000.00
        self.ativo.quantidade = 0.75  # Atualizando a quantidade
        self.ativo.save()

        # Recarregar o ativo do banco de dados para verificar a atualização
        ativo_atualizado = Ativo.objects.get(id=self.ativo.id)
        self.assertEqual(ativo_atualizado.valor_compra, 12000.00)
        self.assertEqual(ativo_atualizado.quantidade, 0.75)  # Verifica a quantidade atualizada

    def test_delete_ativo(self):
        # Teste para deletar um ativo
        self.ativo.delete()
        self.assertEqual(Ativo.objects.count(), 0)  # Deve haver 0 ativos agora

