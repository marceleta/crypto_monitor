from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import CorretoraConfig, TipoOperacao, CorretoraUsuario
from .serializers import CorretoraConfigSerializer, TipoOperacaoSerializer, CorretoraUsuarioSerializer

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


