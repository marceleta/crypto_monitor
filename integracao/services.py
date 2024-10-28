from abc import ABC, abstractmethod
import requests
import time
import hmac
import hashlib

class CorretoraService(ABC):

    def __init__(self, corretoraUsuario):
        self.corretoraUsuario = corretoraUsuario

    @abstractmethod
    def buscar_preco_ativo(self, ativo):
        pass

    @abstractmethod
    def testar_conexao(self):
        pass

    def _fazer_requisicao(self, endpoint, params=None, method='GET', data=None):
        try:
            url = f"{self.corretoraUsuario.corretora.url_base}/{endpoint}"
            headers, params = self.autenticar(endpoint, method, params)
            if method == 'POST':
                response = requests.post(url, headers=headers, params=params, json=data)
            else:
                response = requests.get(url, headers=headers, params=params, timeout=10)
            
            response.raise_for_status()

            # Verifica se há erro de autenticação no corpo da resposta JSON
            resposta_json = response.json()
            if 'ret_code' in resposta_json and resposta_json['ret_code'] == '10004':
                return {'sucesso': False, 'mensagem': 'Erro de autenticação: Chave API inválida.', 'dados': resposta_json}

            return {'sucesso': True, 'mensagem': 'Requisição realizada com sucesso.', 'dados': resposta_json}
            
        except requests.exceptions.Timeout:
            return {'sucesso': False, 'mensagem': 'Erro na requisição: Timeout', 'dados': None}
        except requests.exceptions.RequestException as e:
            return {'sucesso': False, 'mensagem': f'Erro na requisição: {str(e)}', 'dados': None}




    @abstractmethod
    def autenticar(self, endpoint, method, params=None):
        pass


class BybitService(CorretoraService):
    
    def buscar_preco_ativo(self, ativo, data, intervalo='1D'):
        endpoint = "v2/public/kline/list"
        timestamp = int(time.mktime(time.strptime(data, '%Y-%m-%d'))) * 1000
        params = {
            'symbol': ativo,
            'interval': intervalo,
            'from': timestamp
        }
        resposta = self._fazer_requisicao(endpoint, params)
        
        # Verifica se a resposta contém resultados
        if resposta and 'dados' in resposta and 'result' in resposta['dados'] and len(resposta['dados']['result']) > 0:
            candle = resposta['dados']['result'][0]
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

    def buscar_cotacoes_por_intervalo(self, ativo, data_inicial, data_final, intervalo='1D'):
        endpoint = "v2/public/kline/list"
        
        # Converte as datas para timestamp em milissegundos
        timestamp_inicial = int(time.mktime(data_inicial.timetuple())) * 1000
        timestamp_final = int(time.mktime(data_final.timetuple())) * 1000

        params = {
            'symbol': ativo,
            'interval': intervalo,
            'from': timestamp_inicial,
            'to': timestamp_final
        }
        resposta = self._fazer_requisicao(endpoint, params)
        # Verifica se a resposta é válida e contém os dados necessários
        if resposta['dados'] is not None and isinstance(resposta, dict) and 'dados' in resposta and 'result' in resposta['dados']:
            candles = resposta['dados']['result']
            if candles:
                cotacoes = []
                for candle in candles:
                    cotacao = {
                        'abertura': candle['open'],
                        'fechamento': candle['close'],
                        'alta': candle['high'],
                        'baixa': candle['low'],
                        'volume': candle['volume'],
                        'data': time.strftime('%Y-%m-%d', time.gmtime(candle['open_time']))
                    }
                    cotacoes.append(cotacao)

                return cotacoes
            else:
                print(f"Erro: Nenhum dado de candle retornado para o ativo {ativo} no intervalo de {data_inicial} a {data_final}")
                return None
        else:
            print(f"Erro: Resposta inválida ao buscar cotações para o ativo {ativo} no intervalo de {data_inicial} a {data_final}")
            return None


    def autenticar(self, endpoint, method, params=None):
        if params is None:
            params = {}
        timestamp = str(int(time.time() * 1000))
        params['api_key'] = self.corretoraUsuario.api_key
        params['timestamp'] = timestamp
        query_string = '&'.join([f"{key}={params[key]}" for key in sorted(params)])
        signature = hmac.new(self.corretoraUsuario.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        params['sign'] = signature
        return {}, params
    
    def testar_conexao(self):
        resposta = self._fazer_requisicao('v2/public/time')
        if resposta['sucesso'] and 'time_now' in resposta['dados']:
            return True
        return False





