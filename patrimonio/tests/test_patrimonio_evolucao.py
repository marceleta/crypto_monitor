from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from datetime import date
from decimal import Decimal
from usuario.models import Usuario
from moeda.models import Moeda, HistoricoCotacao
from ativo.models import Ativo
from corretora.models import CorretoraConfig, CorretoraUsuario, TipoOperacao
from unittest.mock import patch 

class PatrimonioEvolucaoViewSetTests(APITestCase):

    @patch('integracao.tasks.buscar_cotacoes_task.delay')
    def setUp(self, mock_buscar_cotacoes_task):
        # Mockar a tarefa Celery para evitar execução durante os testes
        mock_buscar_cotacoes_task.return_value = None
        
        # Criar um cliente para realizar requisições
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

        # Criar moedas e associá-las à corretora
        self.moeda_btc = Moeda.objects.create(
            nome='Bitcoin',
            token='BTC',
            usuario=self.usuario,
            corretora=self.corretora_usuario  # Associando a moeda ao CorretoraUsuario criado
        )
        
        self.moeda_eth = Moeda.objects.create(
            nome='Ethereum',
            token='ETH',
            usuario=self.usuario,
            corretora=self.corretora_usuario  # Associando a moeda ao CorretoraUsuario criado
        )
        

        # Criar ativos com data_compra
        Ativo.objects.create(usuario=self.usuario, moeda=self.moeda_btc, quantidade=Decimal('0.5'), valor_compra=Decimal('40000.00'), data_compra=date(2022, 1, 10))
        Ativo.objects.create(usuario=self.usuario, moeda=self.moeda_btc, quantidade=Decimal('0.7'), valor_compra=Decimal('40210.00'), data_compra=date(2022, 2, 11))
        #Ativo.objects.create(usuario=self.usuario, moeda=self.moeda_eth, quantidade=Decimal('2.0'), valor_compra=Decimal('3000.00'), data_compra=date(2022, 1, 15))
        #Ativo.objects.create(usuario=self.usuario, moeda=self.moeda_eth, quantidade=Decimal('1.5'), valor_compra=Decimal('3190.00'), data_compra=date(2022, 2, 17))

        # Criar histórico de cotações para Bitcoin
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 1, 10), abertura=Decimal('40000.00'), fechamento=Decimal('40500.00'), alta=Decimal('41000.00'), baixa=Decimal('39500.00'), volume=Decimal('1200'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 1, 31), abertura=Decimal('40100.00'), fechamento=Decimal('40200.00'), alta=Decimal('40500.00'), baixa=Decimal('40000.00'), volume=Decimal('1300'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 2, 1), abertura=Decimal('40200.00'), fechamento=Decimal('40300.00'), alta=Decimal('40600.00'), baixa=Decimal('40100.00'), volume=Decimal('1400'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 2, 11), abertura=Decimal('40210.00'), fechamento=Decimal('40000.00'), alta=Decimal('40300.00'), baixa=Decimal('39900.00'), volume=Decimal('1100'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 2, 28), abertura=Decimal('39000.00'), fechamento=Decimal('39500.00'), alta=Decimal('40000.00'), baixa=Decimal('38500.00'), volume=Decimal('1250'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 3, 1), abertura=Decimal('41000.00'), fechamento=Decimal('41500.00'), alta=Decimal('42000.00'), baixa=Decimal('40500.00'), volume=Decimal('1400'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 3, 30), abertura=Decimal('42000.00'), fechamento=Decimal('42500.00'), alta=Decimal('43000.00'), baixa=Decimal('41500.00'), volume=Decimal('1500'))
        
        # Criar histórico de cotações para Ethereum
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 1, 15), abertura=Decimal('3000.00'), fechamento=Decimal('3050.00'), alta=Decimal('3100.00'), baixa=Decimal('2950.00'), volume=Decimal('800'))
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 1, 31), abertura=Decimal('3020.00'), fechamento=Decimal('3030.00'), alta=Decimal('3070.00'), baixa=Decimal('3000.00'), volume=Decimal('850'))
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 2, 1), abertura=Decimal('3060.00'), fechamento=Decimal('3080.00'), alta=Decimal('3100.00'), baixa=Decimal('3050.00'), volume=Decimal('900'))
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 2, 28), abertura=Decimal('3100.00'), fechamento=Decimal('3150.00'), alta=Decimal('3200.00'), baixa=Decimal('3050.00'), volume=Decimal('950'))
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 2, 17), abertura=Decimal('3190.00'), fechamento=Decimal('3200.00'), alta=Decimal('3250.00'), baixa=Decimal('3150.00'), volume=Decimal('700'))
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 3, 1), abertura=Decimal('3050.00'), fechamento=Decimal('3100.00'), alta=Decimal('3150.00'), baixa=Decimal('3000.00'), volume=Decimal('850'))
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 3, 31), abertura=Decimal('3100.00'), fechamento=Decimal('3120.00'), alta=Decimal('3150.00'), baixa=Decimal('3080.00'), volume=Decimal('900'))
        
    def test_usuario_sem_ativos(self):
        # Criar um usuário sem ativos
        usuario_sem_ativos = Usuario.objects.create_user(username='user_sem_ativos', password='testpass')
        self.client.force_authenticate(user=usuario_sem_ativos)

        response = self.client.get(reverse('patrimonio-evolucao-evolucao-patrimonio'))
        #print('response: '+str(response.data))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'O usuário não possui ativos')

    def test_evolucao_patrimonio_agrupamento_mensal(self):
        response = self.client.get(reverse('patrimonio-evolucao-evolucao-patrimonio'), {'agrupamento': 'mensal'})
        #print('response.data: '+str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        
        evolucao = response.data['results']
        #print('evolucao: '+str(evolucao))
        # Verificar se o número de períodos retornados está correto (ajustado para paginação)
        self.assertTrue(len(evolucao) <= 12)  # Paginação: no máximo 12 meses

        # Valores esperados para comparação
        expected_evolucao = [
            {'periodo': 'March 2022', 'valor': str(Decimal('2750.00000000000000000000'))},  # Valor inicial pode ser zero
            {'periodo': 'February 2022', 'valor': str(Decimal('-850.00000000000000000000'))},  # Ajuste com base nos dados
            {'periodo': 'January 2022', 'valor': str(Decimal('-150.00000000000000000000'))},    # Ajuste com base nos dados
        ]

        # Comparar os resultados retornados
        for i, expected in enumerate(expected_evolucao):
            self.assertEqual(evolucao[i]['periodo'], expected['periodo'])
            self.assertAlmostEqual(Decimal(evolucao[i]['valor']), Decimal(expected['valor']), places=6)

    def test_evolucao_patrimonio_agrupamento_anual(self):
        response = self.client.get(reverse('patrimonio-evolucao-evolucao-patrimonio'), {'agrupamento': 'anual'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Paginated response
        results = response.data['results']
        #print(results)
       
        # Valores esperados para comparação
        expected_evolucao = [
            {'periodo': '2022', 'valor': str(Decimal('2750.00000000000000000000'))},  # Ajuste com base nos dados
        ]

        # Comparar os resultados retornados
        for i, expected in enumerate(expected_evolucao):
            self.assertEqual(results[i]['periodo'], expected['periodo'])
            self.assertAlmostEqual(Decimal(results[i]['valor']), Decimal(expected['valor']), places=6)

    def test_evolucao_patrimonio_multiples_ativos_mesmo_token(self):
        # Adicionar mais ativos da mesma moeda com data_compra
        #Ativo.objects.create(usuario=self.usuario, moeda=self.moeda_btc, quantidade=Decimal('0.3'), valor_compra=Decimal('22000.00'), data_compra=date(2022, 2, 5))
        #Ativo.objects.create(usuario=self.usuario, moeda=self.moeda_eth, quantidade=Decimal('1.5'), valor_compra=Decimal('1600.00'), data_compra=date(2022, 2, 10))

        # Realizar a requisição à API
        response = self.client.get(reverse('patrimonio-evolucao-evolucao-patrimonio'))
        #print('response: +'+ str(response.data))
        # Verificar o status da resposta
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar se 'results' está presente na resposta paginada
        results = response.data['results']
        

        # Verificar se o número de períodos retornados está correto (ajustado para 3 períodos)
        self.assertEqual(len(results), 3)

        # Verificar se os valores retornados contêm 'valor'
        for item in results:
            self.assertIn('valor', item)

        # Cálculos esperados para mais ativos no mesmo período
        expected_evolucao = [
            {'periodo': 'March 2022', 'valor': str(Decimal('2750.00000000000000000000'))},
            {'periodo': 'February 2022', 'valor': str(Decimal('-850.00000000000000000000'))},
            {'periodo': 'January 2022', 'valor': str(Decimal('-150.00000000000000000000'))},
        ]

        # Comparar os resultados retornados com os valores esperados
        for i, expected in enumerate(expected_evolucao):
            self.assertEqual(results[i]['periodo'], expected['periodo'])
            self.assertAlmostEqual(Decimal(results[i]['valor']), Decimal(expected['valor']), places=6)


    def test_usuario_nao_autenticado(self):
        # Desautenticar o usuário
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse('patrimonio-evolucao-evolucao-patrimonio'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


