from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from datetime import date
from decimal import Decimal
from usuario.models import Usuario
from moeda.models import Moeda, HistoricoCotacao
from ativo.models import Ativo 

class PatrimonioEvolucaoViewSetTests(APITestCase):

    def setUp(self):
        # Criar um cliente para realizar requisições
        self.client = APIClient()

        # Criar um usuário para os testes
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        # Autenticar o usuário
        self.client.force_authenticate(user=self.usuario)

        # Criar moedas
        self.moeda_btc = Moeda.objects.create(nome='Bitcoin', token='BTC', usuario=self.usuario)
        self.moeda_eth = Moeda.objects.create(nome='Ethereum', token='ETH', usuario=self.usuario)

        # Criar ativos com data_compra
        Ativo.objects.create(usuario=self.usuario, moeda=self.moeda_btc, quantidade=Decimal('0.5'), valor_compra=Decimal('40000.00'), data_compra=date(2022, 1, 10))
        Ativo.objects.create(usuario=self.usuario, moeda=self.moeda_btc, quantidade=Decimal('0.7'), valor_compra=Decimal('40210.00'), data_compra=date(2022, 2, 11))
        Ativo.objects.create(usuario=self.usuario, moeda=self.moeda_eth, quantidade=Decimal('2.0'), valor_compra=Decimal('3000.00'), data_compra=date(2022, 1, 15))
        Ativo.objects.create(usuario=self.usuario, moeda=self.moeda_eth, quantidade=Decimal('1.5'), valor_compra=Decimal('3190.00'), data_compra=date(2022, 2, 17))

        # Criar histórico de cotações para Bitcoin
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 1, 10), preco=Decimal('40000.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 1, 31), preco=Decimal('40100.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 2, 1), preco=Decimal('40200.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 2, 11), preco=Decimal('40210.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 2, 28), preco=Decimal('39000.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 3, 1), preco=Decimal('41000.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2022, 3, 31), preco=Decimal('42000.00'))

        # Criar histórico de cotações para Ethereum
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 1, 15), preco=Decimal('3000.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 1, 31), preco=Decimal('3020.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 2, 1), preco=Decimal('3060.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 2, 28), preco=Decimal('3100.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 2, 17), preco=Decimal('3190.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 3, 1), preco=Decimal('3050.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_eth, data=date(2022, 3, 31), preco=Decimal('3100.00'))

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        
        evolucao = response.data['results']
        #print('evolucao: '+str(evolucao))
        # Verificar se o número de períodos retornados está correto (ajustado para paginação)
        self.assertTrue(len(evolucao) <= 12)  # Paginação: no máximo 12 meses

        # Valores esperados para comparação
        expected_evolucao = [
            {'periodo': 'March 2022', 'valor': str(Decimal('2318.00000000000000000000'))},  # Valor inicial pode ser zero
            {'periodo': 'February 2022', 'valor': str(Decimal('-1282.00000000000000000000'))},  # Ajuste com base nos dados
            {'periodo': 'January 2022', 'valor': str(Decimal('90.00000000000000000000'))},    # Ajuste com base nos dados
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
            {'periodo': '2022', 'valor': str(Decimal('2318.00000000000000000000'))},  # Ajuste com base nos dados
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
            {'periodo': 'March 2022', 'valor': str(Decimal('2318.00000000000000000000'))},
            {'periodo': 'February 2022', 'valor': str(Decimal('-1282.00000000000000000000'))},
            {'periodo': 'January 2022', 'valor': str(Decimal('90.00000000000000000000'))},
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


