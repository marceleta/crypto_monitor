import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from corretora.services import BybitService
from corretora.models import CorretoraUsuario, CorretoraConfig
import requests

class TestBybitService(unittest.TestCase):

    def setUp(self):

        # Criação de instância real de CorretoraConfig
        self.corretora_config, created = CorretoraConfig.objects.get_or_create(
            nome="Bybit",
            url_base="https://api.bybit.com",
            exige_passphrase=True
        )
        # Configuração básica para os testes
        self.corretora = CorretoraUsuario(
            api_key="test_api_key",
            api_secret="test_api_secret",
            passphrase="test_passphrase",
            corretora=self.corretora_config
        )
        self.service = BybitService(self.corretora)
        self.ativo = "BTCUSD"
        self.data = "2023-10-01"
    
    @patch('corretora.services.requests.get')  # Mocka a função requests.get para não fazer chamadas reais
    def test_buscar_preco_ativo_sucesso(self, mock_get):
        # Simula uma resposta da API para candles
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'result': [{
                'open': '40000',
                'close': '40500',
                'high': '41000',
                'low': '39500',
                'volume': '1200',
            }]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Chama o método do serviço
        preco = self.service.buscar_preco_ativo(self.ativo, self.data)
        
        # Verifica se a resposta está correta
        self.assertEqual(preco['abertura'], '40000')
        self.assertEqual(preco['fechamento'], '40500')
        self.assertEqual(preco['alta'], '41000')
        self.assertEqual(preco['baixa'], '39500')
        self.assertEqual(preco['volume'], '1200')
        self.assertEqual(preco['data'], self.data)

    @patch('corretora.services.requests.get')
    def test_buscar_preco_ativo_falha(self, mock_get):
        # Simula uma resposta de falha
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': []}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Chama o método do serviço
        preco = self.service.buscar_preco_ativo(self.ativo, self.data)
        
        # Verifica se o retorno é None em caso de falha
        self.assertIsNone(preco)
    
    @patch('corretora.services.requests.get')
    def test_testar_conexao_sucesso(self, mock_get):
        # Simula uma resposta bem-sucedida para o teste de conexão
        mock_response = MagicMock()
        mock_response.json.return_value = {'time_now': '1628475600'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Chama o método de teste de conexão
        result = self.service.testar_conexao()
        
        # Verifica se a conexão foi bem-sucedida
        self.assertTrue(result)

    @patch('corretora.services.requests.get')
    def test_testar_conexao_falha(self, mock_get):
        # Simula uma falha no teste de conexão
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Chama o método de teste de conexão
        result = self.service.testar_conexao()
        
        # Verifica se a conexão falhou
        self.assertFalse(result)

    @patch('corretora.services.requests.get')
    def test_fazer_requisicao_sucesso(self, mock_get):
        # Simula uma resposta bem-sucedida para _fazer_requisicao
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'OK'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Testa o método privado _fazer_requisicao
        response = self.service._fazer_requisicao('v2/public/time')
        self.assertEqual(response['result'], 'OK')

    @patch('corretora.services.requests.get')
    def test_fazer_requisicao_erro(self, mock_get):
        # Simula uma falha na requisição
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Erro de conexão")
        mock_get.return_value = mock_response
        
        # Testa o método privado _fazer_requisicao
        response = self.service._fazer_requisicao('v2/public/time')
        self.assertIsNone(response)
    
