from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import CorretoraConfig, TipoOperacao, CorretoraUsuario
from .serializers import CorretoraConfigSerializer, TipoOperacaoSerializer, CorretoraUsuarioSerializer, CorretoraUsuarioDetailSerializer

# ViewSet para TipoOperacao
class TipoOperacaoViewSet(viewsets.ModelViewSet):
    queryset = TipoOperacao.objects.all()
    serializer_class = TipoOperacaoSerializer

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ViewSet para CorretoraConfig
class CorretoraConfigViewSet(viewsets.ModelViewSet):
    queryset = CorretoraConfig.objects.all()
    serializer_class = CorretoraConfigSerializer

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CorretoraUsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = CorretoraUsuarioSerializer

    # Customiza o queryset para retornar apenas os objetos do usuário autenticado
    def get_queryset(self):
        return CorretoraUsuario.objects.filter(usuario=self.request.user)

    def create(self, request, *args, **kwargs):
        #print('request.data: '+str(request.data))
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    

    # Action personalizada para buscar corretoras pelo nome
    @action(detail=False, methods=['get'], url_path='buscar-por-nome')
    def buscar_por_nome(self, request):
        nome = request.query_params.get('nome', None)
        if nome:
            corretoras = CorretoraUsuario.objects.filter(usuario=self.request.user, corretora__nome__icontains=nome)
            serializer = self.get_serializer(corretoras, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "Nome do corretor não fornecido."}, status=status.HTTP_400_BAD_REQUEST)
    

class CorretoraUsuarioDetailViewSet(viewsets.ModelViewSet):
    serializer_class = CorretoraUsuarioDetailSerializer  # Usa o serializer detalhado

    # Customiza o queryset para retornar apenas os objetos do usuário autenticado
    def get_queryset(self):
        return CorretoraUsuario.objects.filter(usuario=self.request.user).prefetch_related('tipos', 'corretora__tipos_suportados')

    def retrieve(self, request, *args, **kwargs):
        """
        Sobrescreve o método retrieve para retornar os detalhes de CorretoraUsuario e CorretoraConfig
        """
        instance = self.get_object()  # Obtém a instância pelo ID filtrado pelo usuário
        serializer = self.get_serializer(instance)  # Serializa com o serializer detalhado
        return Response(serializer.data, status=status.HTTP_200_OK)


