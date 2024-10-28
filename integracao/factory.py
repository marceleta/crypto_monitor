from integracao.services import BybitService

class CorretoraServiceFactory:
    """
    Factory para criar o serviço correto de acordo com a corretora.
    """

    @staticmethod
    def criar_servico(corretora_usuario):
        nome_corretora = (corretora_usuario.corretora.nome).lower()
        if nome_corretora == 'bybit':
            return BybitService(corretora_usuario)
        else:
            raise ValueError(f"Serviço para a corretora {corretora_usuario.corretora.nome} não é suportado.")