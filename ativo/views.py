from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Ativo
from .serializers import AtivoSerializer

class AtivoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Ativos.
    CRUD completo: list, retrieve, create, update, delete.
    A permissão de autenticação é necessária para todas as ações.
    O usuário autenticado é automaticamente associado ao Ativo.
    """
    serializer_class = AtivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Sobrescreve o queryset para garantir que apenas os ativos do usuário autenticado
        sejam retornados.
        """
        return Ativo.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        """
        Sobrescreve a criação para associar automaticamente o usuário autenticado ao Ativo.
        """
        #print("AtivoViewSet perform_create"+str(serializer))
        
        serializer.save(usuario=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Sobrescreve o método create para retornar uma resposta personalizada em caso de sucesso.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """
        Sobrescreve o método update para garantir que o usuário autenticado seja sempre o mesmo.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Garantir que o usuário autenticado não seja alterado no update
        if 'usuario' in request.data and request.data['usuario'] != instance.usuario.id:
            return Response({"detail": "Você não pode alterar o usuário do ativo."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Sobrescreve o método destroy para adicionar uma resposta personalizada.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Ativo deletado com sucesso!"}, status=status.HTTP_204_NO_CONTENT)

