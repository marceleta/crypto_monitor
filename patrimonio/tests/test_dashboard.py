from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ativo.models import Ativo
from moeda.models import Moeda, HistoricoCotacao
from corretora.models import CorretoraConfig, CorretoraUsuario, TipoOperacao
from usuario.models import Usuario
from decimal import Decimal
from datetime import date  # Importante para definir a data de compra
from ativo.signals import iniciar_busca_apos_criacao_ativo
from django.db.models.signals import post_save

class DashboardViewSetTests(TestCase):

    def setUp(self):
        # Desconectar o sinal para evitar execução durante os testes
        post_save.disconnect(iniciar_busca_apos_criacao_ativo, sender=Ativo)
        
        # Criar o cliente para realizar requisições
        self.client = APIClient()

        # Criar um usuário para os testes
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        # Autenticar o usuário
        self.client.force_authenticate(user=self.usuario)

        # Criar a configuração da corretora
        self.corretora_config = CorretoraConfig.objects.create(
            nome="Bybit",
            url_base="https://api.bybit.com",
            exige_passphrase=False
        )

        # Criar tipos de operação
        self.tipo_spot = TipoOperacao.objects.create(tipo='spot')

        # Associar os tipos de operação à corretora
        self.corretora_config.tipos_suportados.add(self.tipo_spot)

        # Criar a associação entre o usuário e a corretora
        self.corretora_usuario = CorretoraUsuario.objects.create(
            corretora=self.corretora_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            passphrase=None,
            usuario=self.usuario
        )

        # Associar tipos de operação ao CorretoraUsuario
        self.corretora_usuario.tipos.add(self.tipo_spot)

        # Criar moedas associadas à corretora
        self.moeda_btc = Moeda.objects.create(
            nome='Bitcoin',
            token='BTC',
            cor='#F7931A',
            logo=None,
            usuario=self.usuario,
            corretora=self.corretora_usuario
        )
        self.moeda_eth = Moeda.objects.create(
            nome='Ethereum',
            token='ETH',
            cor='#3C3C3D',
            logo=None,
            usuario=self.usuario,
            corretora=self.corretora_usuario
        )

        # Criar ativos para o usuário, incluindo 'data_compra'
        Ativo.objects.create(
            moeda=self.moeda_btc,
            quantidade=1.5,
            valor_compra=Decimal('30000.00'),
            data_compra=date(2024, 1, 1),
            usuario=self.usuario
        )
        Ativo.objects.create(
            moeda=self.moeda_eth,
            quantidade=10,
            valor_compra=Decimal('15000.00'),
            data_compra=date(2024, 1, 15),
            usuario=self.usuario
        )

        # Criar histórico de cotações para as moedas com os novos campos
        HistoricoCotacao.objects.create(
            moeda=self.moeda_btc,
            data=date(2024, 1, 5),
            abertura=Decimal('34000.00'),
            fechamento=Decimal('35000.00'),
            alta=Decimal('35500.00'),
            baixa=Decimal('33000.00'),
            volume=Decimal('1500')
        )
        HistoricoCotacao.objects.create(
            moeda=self.moeda_eth,
            data=date(2024, 1, 20),
            abertura=Decimal('1700.00'),
            fechamento=Decimal('1800.00'),
            alta=Decimal('1850.00'),
            baixa=Decimal('1650.00'),
            volume=Decimal('1000')
        )

    def test_grafico_distribuicao_ativos(self):
        # Realizar a requisição GET para o endpoint
        response = self.client.get('/api/v1/dashboard/grafico_distribuicao_ativos/')
        #print(response.data)
        # Verificar se o status da resposta é 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar se o valor total da carteira foi calculado corretamente
        valor_total_carteira = Decimal('1.5') * Decimal('35000.00') + Decimal('10') * Decimal('1800.00')
        self.assertEqual(response.data['valor_total_carteira'], float(valor_total_carteira))

        # Verificar se a distribuição dos ativos está correta
        distribuicao = response.data['distribuicao']
        self.assertEqual(len(distribuicao), 2)  # Deve haver 2 ativos no total

        # Verificar os valores individuais de Bitcoin e Ethereum
        for ativo in distribuicao:
            if ativo['moeda'] == 'Bitcoin':
                self.assertEqual(ativo['quantidade_total'], 1.5)
                self.assertEqual(Decimal(ativo['valor_total']), Decimal(1.5) * Decimal('35000.00'))
            elif ativo['moeda'] == 'Ethereum':
                self.assertEqual(ativo['quantidade_total'], 10)
                self.assertEqual(Decimal(ativo['valor_total']), Decimal(10) * Decimal('1800.00'))

        # Verificar se a soma das porcentagens é 100%
        percentual_total = sum([ativo['percentual'] for ativo in distribuicao])
        self.assertAlmostEqual(percentual_total, 100, places=2)

    def test_grafico_distribuicao_ativos_sem_ativos(self):
        # Criar um novo usuário que não possui ativos
        usuario_sem_ativos = Usuario.objects.create_user(username='no_assets', password='testpass')
        self.client.force_authenticate(user=usuario_sem_ativos)

        # Realizar a requisição GET para o endpoint
        response = self.client.get('/api/v1/dashboard/grafico_distribuicao_ativos/')
        #print(response.data)
        # Verificar se o status da resposta é 200 OK e a carteira é zero
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['valor_total_carteira'], 0)
        self.assertEqual(len(response.data['distribuicao']), 0)

    def test_usuario_nao_autenticado(self):
        # Desautenticar o usuário
        self.client.force_authenticate(user=None)

        # Realizar a requisição GET para o endpoint
        response = self.client.get('/api/v1/dashboard/grafico_distribuicao_ativos/')
        #print(response.data)
        # Verificar se o status da resposta é 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

