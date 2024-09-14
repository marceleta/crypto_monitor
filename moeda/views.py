from rest_framework import viewsets
from moeda.models import Moeda
from moeda.serializers import MoedaSerializer
from rest_framework.permissions import IsAuthenticated  # Certifique-se de que a autenticação é obrigatória

class MoedaViewSet(viewsets.ModelViewSet):
    queryset = Moeda.objects.all()
    serializer_class = MoedaSerializer
    permission_classes = [IsAuthenticated]  # Garante que a autenticação é necessária

    def perform_create(self, serializer):
        # Associa a moeda ao usuário autenticado
        #print("request.user: "+str(self.request.user))
        serializer.save(usuario=self.request.user)


