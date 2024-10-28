from django.test import TestCase
from unittest.mock import patch, MagicMock
from integracao.services import BybitService
from corretora.models import CorretoraUsuario, CorretoraConfig
import requests
from usuario.models import Usuario
from datetime import datetime

class TestBybitService(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Criação de um usuário para ser usado nos testes
        cls.usuario = Usuario.objects.create_user(username='testuser', password='12345')
        
        # Criação de instância real de CorretoraConfig
        cls.corretora_config, created = CorretoraConfig.objects.get_or_create(
            nome="Bybit",
            url_base="https://api.bybit.com",
            exige_passphrase=True
        )

    def setUp(self):
        # Configuração básica para os testes
        self.corretora = CorretoraUsuario(
            api_key="test_api_key",
            api_secret="test_api_secret",
            passphrase="test_passphrase",
            corretora=self.corretora_config,
            usuario=self.usuario
        )
        self.corretora.save()  # Salva a instância no banco de dados
        self.service = BybitService(self.corretora)
        self.ativo = "BTCUSD"
        self.data_inicial = "2023-10-01"
        self.data_final = "2023-10-05"

    @patch('integracao.services.requests.get')
    def test_buscar_cotacoes_por_intervalo_sucesso(self, mock_get):
        # Simula uma resposta da API com dados para várias datas
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'result': [
                {'open': '40000', 'close': '40500', 'high': '41000', 'low': '39500', 'volume': '1200', 'open_time': 1696204800},
                {'open': '40500', 'close': '40700', 'high': '41500', 'low': '40000', 'volume': '1300', 'open_time': 1696291200},
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Converte as strings para objetos datetime.date
        data_inicial = datetime.strptime(self.data_inicial, '%Y-%m-%d').date()
        data_final = datetime.strptime(self.data_final, '%Y-%m-%d').date()

        # Chama o método do serviço
        cotacoes = self.service.buscar_cotacoes_por_intervalo(self.ativo, data_inicial, data_final)

        # Verifica se a resposta está correta
        self.assertEqual(len(cotacoes), 2)
        self.assertEqual(cotacoes[0]['abertura'], '40000')
        self.assertEqual(cotacoes[0]['fechamento'], '40500')
        self.assertEqual(cotacoes[0]['alta'], '41000')
        self.assertEqual(cotacoes[0]['baixa'], '39500')
        self.assertEqual(cotacoes[0]['volume'], '1200')
        self.assertEqual(cotacoes[0]['data'], '2023-10-02')

        self.assertEqual(cotacoes[1]['abertura'], '40500')
        self.assertEqual(cotacoes[1]['fechamento'], '40700')
        self.assertEqual(cotacoes[1]['alta'], '41500')
        self.assertEqual(cotacoes[1]['baixa'], '40000')
        self.assertEqual(cotacoes[1]['volume'], '1300')
        self.assertEqual(cotacoes[1]['data'], '2023-10-03')

    @patch('integracao.services.requests.get')
    def test_buscar_cotacoes_por_intervalo_vazio(self, mock_get):
        # Simula uma resposta vazia da API
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': []}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Converte as strings para objetos datetime.date
        data_inicial = datetime.strptime(self.data_inicial, '%Y-%m-%d').date()
        data_final = datetime.strptime(self.data_final, '%Y-%m-%d').date()

        # Chama o método do serviço
        cotacoes = self.service.buscar_cotacoes_por_intervalo(self.ativo, data_inicial, data_final)

        # Verifica se o retorno é None para resultado vazio
        self.assertIsNone(cotacoes)

    @patch('integracao.services.requests.get')
    def test_buscar_cotacoes_por_intervalo_falha(self, mock_get):
        # Simula uma falha na requisição
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Erro de conexão")
        mock_get.return_value = mock_response

        # Converte as strings para objetos datetime.date
        data_inicial = datetime.strptime(self.data_inicial, '%Y-%m-%d').date()
        data_final = datetime.strptime(self.data_final, '%Y-%m-%d').date()

        # Chama o método do serviço
        cotacoes = self.service.buscar_cotacoes_por_intervalo(self.ativo, data_inicial, data_final)

        # Verifica se o retorno é None para falha na requisição
        self.assertIsNone(cotacoes)

    @patch('integracao.services.requests.get')
    def test_buscar_cotacoes_por_intervalo_erro_autenticacao(self, mock_get):
        # Simula um erro de autenticação
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"ret_code": "10004", "ret_msg": "Invalid API key"}
        mock_get.return_value = mock_response

        # Converte as strings para objetos datetime.date
        data_inicial = datetime.strptime(self.data_inicial, '%Y-%m-%d').date()
        data_final = datetime.strptime(self.data_final, '%Y-%m-%d').date()


        # Chama o método do serviço
        cotacoes = self.service.buscar_cotacoes_por_intervalo(self.ativo, data_inicial, data_final)

        # Verifica se o retorno é None para erro de autenticação
        self.assertIsNone(cotacoes)



    
