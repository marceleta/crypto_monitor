import requests
from abc import ABC, abstractmethod

class CorretoraService(ABC):
    
    @abstractmethod
    def get_precos(self, symbol):
        """
        Retorna os preços atuais de um ativo (ex: BTC/USDT).
        """
        pass

    @abstractmethod
    def get_saldo(self):
        """
        Retorna o saldo disponível na corretora para cada moeda.
        """
        pass

    @abstractmethod
    def get_historico_transacoes(self):
        """
        Retorna o histórico de transações de compra e venda.
        """
        pass


class BybitService(CorretoraService):
    
    def __init__(self, corretora):
        """
        A corretora é uma instância de BybitCorretora que contém as chaves da API.
        """
        self.api_key = corretora.api_key
        self.api_secret = corretora.api_secret
        self.base_url = 'https://api.bybit.com'
    
    def get_precos(self, symbol):
        try:
            response = requests.get(f'{self.base_url}/v2/public/tickers?symbol={symbol}')
            response.raise_for_status()  # Levanta uma exceção para códigos de erro HTTP
            data = response.json()
            return data['result'][0]['last_price']
        except requests.RequestException as e:
            # Tratar erro de conexão ou erro HTTP
            #print(f"Erro ao buscar preço: {e}")
            return None


    def get_saldo(self):
        url = f'{self.base_url}/v2/private/wallet/balance'
        params = {'api_key': self.api_key}
        return self._get(url, params=params)

    def get_historico_transacoes(self):
        url = f'{self.base_url}/v2/private/execution/list'
        params = {'api_key': self.api_key}
        return self._get(url, params=params)
    
    def _get(self, url, params=None):
        """
        Método privado que encapsula a lógica de fazer uma requisição GET
        e de tratar erros básicos.
        """
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Lança um erro para status HTTP 4xx/5xx
            data = response.json()
            return data['result']
        except requests.exceptions.HTTPError as e:
            # Trate erros HTTP aqui
            print(f"Erro HTTP: {e}")
        except requests.exceptions.RequestException as e:
            # Trate outros erros (ex. de conexão)
            print(f"Erro de conexão: {e}")
        except KeyError:
            # Tratar erros de formato inesperado na resposta
            print("Erro: resposta inesperada da API.")


