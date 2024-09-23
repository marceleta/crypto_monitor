from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from moeda.models import Moeda, HistoricoCotacao
from usuario.models import Usuario  # Ou o modelo de usuário que você está usando
from decimal import Decimal
from datetime import date

class AtivoDetalheViewSetTests(TestCase):

    def setUp(self):
        # Criar o cliente para realizar requisições
        self.client = APIClient()

        # Criar um usuário para os testes
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        # Autenticar o usuário
        self.client.force_authenticate(user=self.usuario)

        # Criar uma moeda para associar aos históricos
        self.moeda_btc = Moeda.objects.create(nome='Bitcoin', token='BTC', cor='#F7931A', logo=None, usuario=self.usuario)

        # Criar histórico de cotações em meses diferentes
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2024, 1, 5), preco=Decimal('35000.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2024, 2, 12), preco=Decimal('35500.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2024, 3, 18), preco=Decimal('36000.00'))
        HistoricoCotacao.objects.create(moeda=self.moeda_btc, data=date(2024, 4, 25), preco=Decimal('36500.00'))


    def test_historico_preco_agrupamento_mensal(self):
        # Fazer uma requisição para o endpoint de agrupamento mensal
        response = self.client.get(
            f'/api/v1/ativo-detalhe/{self.moeda_btc.id}/historico_preco/',
            {'agrupamento': 'mensal'}
        )
        #print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('historico', response.data)
        self.assertEqual(len(response.data['historico']), 4)  # Deve haver 4 agrupamentos mensais

        # Ordenar o histórico por data para garantir a ordem
        historico = response.data['historico']
        historico.sort(key=lambda x: x['data'])

        # Preparar os dados esperados
        expected_data = [
            {
                'data': date(2024, 1, 1),
                'preco': Decimal('35000.00')
            },
            {
                'data': date(2024, 2, 1),
                'preco': Decimal('35500.00')
            },
            {
                'data': date(2024, 3, 1),
                'preco': Decimal('36000.00')
            },
            {
                'data': date(2024, 4, 1),
                'preco': Decimal('36500.00')
            },
        ]

        # Verificar cada entrada do histórico retornado
        for i, expected in enumerate(expected_data):
            self.assertEqual(historico[i]['data'], expected['data'])
            self.assertEqual(Decimal(str(historico[i]['preco'])), expected['preco'])


        
    def test_historico_preco_agrupamento_semanal(self):
        # Realizar a requisição GET para o endpoint de histórico de preços (agrupamento semanal)
        response = self.client.get(
            f'/api/v1/ativo-detalhe/{self.moeda_btc.pk}/historico_preco/',
            {'agrupamento': 'semanal'}
        )

        # Verificar se o status da resposta é 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar se o histórico retornado contém os valores corretos
        historico = response.data['historico']
        self.assertEqual(len(historico), 4)  # Deve haver 4 semanas com cotações


    def test_historico_preco_filtro_periodo(self):
        # Realizar a requisição GET filtrando por um intervalo de datas

        response = self.client.get(
            f'/api/v1/ativo-detalhe/{self.moeda_btc.pk}/historico_preco/',
            {'data_inicio': '2024-01-01', 'data_fim': '2024-04-30'}
        )
        #print(response.data)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar se o histórico retornado contém todas as 4 entradas no período
        historico = response.data['historico']
        self.assertEqual(len(historico), 4) 

        # Opcional: Verificar os preços das cotações retornadas
        precos_esperados = [
        Decimal('35000.00'),
        Decimal('35500.00'),
        Decimal('36000.00'),
        Decimal('36500.00')
        ]
        precos_retornados = [Decimal(str(item['preco'])) for item in historico]
        self.assertEqual(precos_retornados, precos_esperados)


    def test_moeda_nao_encontrada_para_usuario(self):
        # Criar outro usuário que não possui a moeda
        outro_usuario = Usuario.objects.create_user(username='otheruser', password='testpass')
        self.client.force_authenticate(user=outro_usuario)

        # Realizar a requisição GET para o endpoint de histórico de preços
        response = self.client.get(f'/api/v1/ativo-detalhe/{self.moeda_btc.pk}/historico_preco/')

        # Verificar se o status da resposta é 404 Not Found, já que a moeda não pertence a este usuário
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_usuario_nao_autenticado(self):
        # Desautenticar o usuário
        self.client.force_authenticate(user=None)

        # Realizar a requisição GET para o endpoint de histórico de preços
        response = self.client.get(f'/api/v1/ativo-detalhe/{self.moeda_btc.pk}/historico_preco/')

        # Verificar se o status da resposta é 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_historico_preco_agrupamento_quinzenal(self):
        # Realizar a requisição GET para o endpoint com agrupamento quinzenal
        response = self.client.get(
            f'/api/v1/ativo-detalhe/{self.moeda_btc.pk}/historico_preco/',
            {'agrupamento': 'quinzenal'}
        )
        #print(response.data)
        # Verificar se o status da resposta é 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar se o histórico retornado contém os valores corretos
        historico = response.data['historico']
        self.assertEqual(len(historico), 4)  # Deve haver 4 quinzenas

        # Ordenar o histórico por mes e quinzena para garantir a ordem
        historico.sort(key=lambda x: (x['mes'], x['quinzena']))

        # Preparar os dados esperados
        expected_data = [
            {
                'mes': date(2024, 1, 1),
                'quinzena': 1,
                'preco': Decimal('35000.00')
            },
            {
                'mes': date(2024, 2, 1),
                'quinzena': 1,
                'preco': Decimal('35500.00')
            },
            {
                'mes': date(2024, 3, 1),
                'quinzena': 2,
                'preco': Decimal('36000.00')
            },
            {
                'mes': date(2024, 4, 1),
                'quinzena': 2,
                'preco': Decimal('36500.00')
            },
        ]

        # Verificar cada entrada do histórico retornado
        for i, expected in enumerate(expected_data):
            self.assertEqual(historico[i]['mes'], expected['mes'])
            self.assertEqual(historico[i]['quinzena'], expected['quinzena'])
            self.assertEqual(Decimal(str(historico[i]['preco'])), expected['preco'])


