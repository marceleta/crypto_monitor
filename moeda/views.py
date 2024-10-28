from rest_framework import viewsets
from ativo.models import Ativo
from moeda.models import Moeda, HistoricoCotacao
from moeda.serializers import MoedaSerializer, HistoricoCotacaoSerializer
from rest_framework.permissions import IsAuthenticated  # Certifique-se de que a autenticação é obrigatória
from rest_framework.response import Response
from rest_framework.decorators import action
from collections import defaultdict

class MoedaViewSet(viewsets.ModelViewSet):
    queryset = Moeda.objects.all()
    serializer_class = MoedaSerializer
    permission_classes = [IsAuthenticated]  # Garante que a autenticação é necessária

    def get_queryset(self):
        # Retorna apenas as moedas associadas ao usuário autenticado
        return Moeda.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        # Associa a moeda ao usuário autenticado
        #print("request.user: "+str(self.request.user))
        #print('Moeda Serializer: '+str(serializer))
        serializer.save(usuario=self.request.user)





