from abc import ABC, abstractmethod
import requests
import time
import hmac
import hashlib


class CorretoraService(ABC):

    def __init__(self, corretora):
        self.corretora = corretora

    @abstractmethod
    def buscar_preco_ativo(self, ativo):
        pass

    @abstractmethod
    def testar_conexao(self):
        pass

    def _fazer_requisicao(self, endpoint, params=None, method='GET', data=None):
        try:
            url = f"{self.corretora.url_base}/{endpoint}"
            headers, params = self.autenticar(endpoint, method, params)
            if method == 'POST':
                response = requests.post(url, headers=headers, params=params, json=data)
            else:
                response = requests.get(url, headers=headers, params=params, timeout=10)
            
            response.raise_for_status()  # Levanta exceção para erros de status HTTP
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return None



    @abstractmethod
    def autenticar(self, endpoint, method, params=None):
        pass
    

class BybitService(CorretoraService):
    
    def buscar_preco_ativo(self, ativo, data, intervalo='1D'):
        # Endpoint para candles históricos
        endpoint = "v2/public/kline/list"
        
        # Converter a data desejada para timestamp (em segundos)
        timestamp = int(time.mktime(time.strptime(data, '%Y-%m-%d'))) * 1000  # Milissegundos

        
        # Parâmetros da requisição
        params = {
            'symbol': ativo,  # Ex: BTCUSD
            'interval': intervalo,  # Ex: 1, 3, 5, 15, 30, 60 (minutos), D (diário)
            'from': timestamp  # Timestamp de início
        }

        # Fazer a requisição para o endpoint de velas
        resposta = self._fazer_requisicao(endpoint, params)
        
        # Verificar se há dados retornados e pegar o primeiro candle da resposta
        if 'result' in resposta and len(resposta['result']) > 0:
            candle = resposta['result'][0]  # Candle mais próximo da data
            return {
                'abertura': candle['open'],
                'fechamento': candle['close'],
                'alta': candle['high'],
                'baixa': candle['low'],
                'volume': candle['volume'],
                'data': data
            }
        else:
            print(f"Erro: Nenhum dado de candle retornado para o ativo {ativo} na data {data}")
            return None

    def autenticar(self, endpoint, method, params=None):
        timestamp = str(int(time.time() * 1000))
        params['api_key'] = self.corretora.api_key
        params['timestamp'] = timestamp
        query_string = '&'.join([f"{key}={params[key]}" for key in sorted(params)])
        signature = hmac.new(self.corretora.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        params['sign'] = signature
        return {}, params # Retorna headers vazios, pois Bybit utiliza params
    

    def testar_conexao(self):
        """
        Método para testar a conexão com a API da Bybit.
        Faz uma requisição simples a um endpoint público para verificar a disponibilidade da API.
        """
        endpoint = "v2/public/time"  # Um endpoint simples que retorna o tempo do servidor
        resposta = self._fazer_requisicao(endpoint)
        if resposta and 'time_now' in resposta:
            print("Conexão com a Bybit bem-sucedida.")
            return True
        else:
            print("Falha na conexão com a Bybit.")
            return False


