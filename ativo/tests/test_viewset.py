from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from ativo.models import Ativo
from moeda.models import Moeda
from usuario.models import Usuario
from corretora.models import CorretoraConfig, CorretoraUsuario  # Import necessário para corretora
from rest_framework_simplejwt.tokens import RefreshToken  # Import necessário para JWT

from django.db.models.signals import post_save
from ativo.signals import iniciar_busca_apos_criacao_ativo

from decimal import Decimal

class AtivoViewSetTests(APITestCase):

    def setUp(self):
        # Cria um usuário e gera o token JWT
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        post_save.disconnect(iniciar_busca_apos_criacao_ativo, sender=Ativo)

        # Gera o token de acesso para o usuário
        refresh = RefreshToken.for_user(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        # Cria a configuração da corretora
        self.corretora_config = CorretoraConfig.objects.create(
            nome="Bybit",
            url_base="https://api.bybit.com",
            exige_passphrase=False
        )

        # Cria a associação entre o usuário e a corretora
        self.corretora_usuario = CorretoraUsuario.objects.create(
            corretora=self.corretora_config,
            api_key="fake_key",
            api_secret="fake_secret",
            usuario=self.usuario
        )

        # Cria uma moeda para ser associada aos ativos
        self.moeda = Moeda.objects.create(
            nome="Bitcoin",
            token="BTC",
            cor="#F7931A",
            logo=None,
            usuario=self.usuario,
            corretora=self.corretora_usuario  # Associando a moeda ao CorretoraUsuario criado
        )

        # Cria um ativo inicial para os testes
        self.ativo = Ativo.objects.create(
            moeda=self.moeda,
            data_compra="2024-09-12",
            valor_compra=10000.00,
            usuario=self.usuario,
            quantidade=0.5
        )

        # URL para a lista de ativos
        self.list_url = reverse('ativo-list')

    def test_create_ativo(self):
        """
        Testa a criação de um novo ativo com o usuário autenticado.
        """
        data = {
            'moeda_id': self.moeda.id,
            'data_compra': '2024-09-11',
            'valor_compra': 5000.00
        }

        # A requisição já estará autenticada devido ao token JWT no cabeçalho
        response = self.client.post(self.list_url, data, format='json')
        #print('test_create_ativo response.data'+str(response.data))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ativo.objects.count(), 2)
        novo_ativo = Ativo.objects.get(data_compra='2024-09-11')
        self.assertEqual(novo_ativo.moeda, self.moeda)
        self.assertEqual(novo_ativo.valor_compra, 5000.00)
        self.assertEqual(novo_ativo.usuario, self.usuario)

    def test_list_ativos(self):
        """
        Testa se o usuário autenticado pode listar os ativos que pertencem a ele.
        """
        response = self.client.get(self.list_url, format='json')
        #print('test_list_ativos response.data: '+str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Deve haver 1 ativo no início
        self.assertEqual(response.data[0]['moeda']['id'], self.moeda.id)

    def test_retrieve_ativo(self):
        """
        Testa se o usuário autenticado pode recuperar os detalhes de um ativo específico.
        """
        ativo_url = reverse('ativo-detail', args=[self.ativo.id])
        response = self.client.get(ativo_url, format='json')
        #print('test_retrieve_ativo response.data: '+str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['moeda']['id'], self.moeda.id)
        self.assertEqual(response.data['valor_compra'], '10000.00')

    def test_update_ativo(self):
        """
        Testa a atualização de um ativo existente, garantindo que o usuário autenticado seja o mesmo.
        """
        ativo_url = reverse('ativo-detail', args=[self.ativo.id])
        data = {
            'moeda_id': self.moeda.id,
            'data_compra': '2024-09-15',
            'valor_compra': Decimal(12000)
        }
        response = self.client.put(ativo_url, data, format='json')
        #print('test_update_ativo response.data: '+str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ativo.refresh_from_db()
        self.assertEqual(Decimal(response.data['valor_compra']), data['valor_compra'])

    def test_delete_ativo(self):
        """
        Testa a exclusão de um ativo existente.
        """
        ativo_url = reverse('ativo-detail', args=[self.ativo.id])
        response = self.client.delete(ativo_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ativo.objects.count(), 0)



