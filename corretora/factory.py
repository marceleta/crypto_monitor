from corretora.services import BybitService

class CorretoraServiceFactory:
    """
    Factory para criar o serviço correto de acordo com a corretora.
    """

    @staticmethod
    def criar_servico(corretora):
        if corretora.nome == 'bybit':
            return BybitService(corretora)
        else:
            raise ValueError(f"Serviço para a corretora {corretora.nome} não é suportado.")