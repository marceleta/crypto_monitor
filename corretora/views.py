from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from .models import Corretora
from .serializers import CorretoraSerializer
from .factory import CorretoraServiceFactory
from moeda.models import HistoricoCotacao, Moeda
from moeda.serializers import HistoricoCotacaoSerializer

class CorretoraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar corretoras. Exige que o usuário esteja autenticado.
    O usuário só pode ver e manipular suas próprias corretoras.
    """
    serializer_class = CorretoraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retorna corretoras associadas ao usuário autenticado.
        """
        return Corretora.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        """
        Define o usuário autenticado como o proprietário da corretora ao criar.
        """
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        """
        Define o usuário autenticado como o proprietário da corretora ao atualizar.
        (Isso garante que o usuário não possa alterar a corretora para outro usuário)
        """
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated])
    def teste_conexao(self, request, pk=None):
        """
        Endpoint customizado para testar a conexão com a API da corretora.
        """
        corretora = self.get_object()
        try:
            # Criar o serviço correto para a corretora usando o factory
            servico = CorretoraServiceFactory.criar_servico(corretora)
            sucesso = servico.testar_conexao()
            if sucesso:
                return Response({'status': 'Conexão OK'}, status=status.HTTP_200_OK)
            return Response({'status': 'Falha na Conexão'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def buscar_preco_ativo(self, request, pk=None):
        """
        Endpoint customizado para recuperar o preço de um ativo e salvar no banco de dados (usando HistoricoCotacao).
        """
        corretora = self.get_object()
        ativo = request.data.get('ativo')
        data = request.data.get('data')

        if not ativo or not data:
            return Response({'erro': 'Ativo e data são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verificar se o ativo corresponde a uma moeda cadastrada
            moeda = Moeda.objects.filter(nome=ativo).first()
            if not moeda:
                return Response({'erro': 'Moeda não encontrada'}, status=status.HTTP_404_NOT_FOUND)

            # Criar o serviço correto para a corretora usando o factory
            servico = CorretoraServiceFactory.criar_servico(corretora)
            preco_ativo = servico.buscar_preco_ativo(ativo, data)

            if preco_ativo:
                # Salvar os dados no banco de dados no modelo HistoricoCotacao
                historico, created = HistoricoCotacao.objects.update_or_create(
                    moeda=moeda,
                    data=data,
                    defaults={'preco': preco_ativo['fechamento']}
                )
                
                # Retornar os dados ao frontend
                serializer = HistoricoCotacaoSerializer(historico)
                return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

            return Response({'erro': 'Falha ao recuperar o preço do ativo'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError as e:
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)

