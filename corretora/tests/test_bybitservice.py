from django.test import TestCase
from unittest.mock import patch
from corretora.services import BybitService
from corretora.models import BybitCorretora
import requests

class BybitServiceTest(TestCase):
    
    @patch('requests.get')
    def test_get_precos(self, mock_get):
        # Mock a resposta da API
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'result': [{'last_price': '50000.00'}]}
        
        corretora = BybitCorretora(api_key='api_key', api_secret='api_secret')
        service = BybitService(corretora)
        
        preco = service.get_precos('BTC/USDT')
        self.assertEqual(preco, '50000.00')

    @patch('requests.get')
    def test_get_precos_api_fails(self, mock_get):
        # Simula uma falha da API
        mock_get.side_effect = requests.exceptions.ConnectionError
        
        corretora = BybitCorretora(api_key='api_key', api_secret='api_secret')
        service = BybitService(corretora)
        
        preco = service.get_precos('BTC/USDT')
        self.assertIsNone(preco)
