from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from moeda.models import Moeda
from usuario.models import Usuario
from rest_framework_simplejwt.tokens import RefreshToken

class MoedaViewSetTests(APITestCase):

    def setUp(self):
        # Cria um usuário e gera o token JWT
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        # Gera o token de acesso para o usuário
        refresh = RefreshToken.for_user(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        # Cria uma moeda inicial para os testes associada ao usuário
        self.moeda = Moeda.objects.create(
            nome="Bitcoin",
            token="BTC",
            cor="#F7931A",
            logo=None,
            usuario=self.usuario  # Associando a moeda ao usuário criado
        )
        self.list_url = reverse('moeda-list')  # URL da lista de moedas

    def test_create_moeda(self):
        # Teste para criação de uma nova moeda
        data = {
            'nome': 'Ethereum',
            'token': 'ETH',
            'cor': '#3C3C3D',
            'logo': None,
            'usuario':self.usuario.id
        }
        response = self.client.post(self.list_url, data, format='json')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Moeda.objects.count(), 2)
        nova_moeda = Moeda.objects.get(token='ETH')
        self.assertEqual(nova_moeda.nome, 'Ethereum')
        self.assertEqual(nova_moeda.usuario, self.usuario)  # Verifica o usuário associado

    def test_list_moedas(self):
        # Teste para listar todas as moedas
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Deve haver 1 moeda no início
        self.assertEqual(response.data[0]['nome'], 'Bitcoin')
        self.assertEqual(response.data[0]['usuario'], self.usuario.id)  # Verificando o usuário associado

    def test_retrieve_moeda(self):
        # Teste para recuperar os detalhes de uma moeda específica
        moeda_url = reverse('moeda-detail', args=[self.moeda.id])
        response = self.client.get(moeda_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Bitcoin')
        self.assertEqual(response.data['usuario'], self.usuario.id)  # Verificando o usuário associado

    def test_update_moeda(self):
        # Teste para atualizar uma moeda existente
        moeda_url = reverse('moeda-detail', args=[self.moeda.id])
        data = {
            'nome': 'Bitcoin Atualizado',
            'token': 'BTC',
            'cor': '#F7931A',
            'logo': None,
            'usuario': self.usuario.id
        }
        response = self.client.put(moeda_url, data, format='json')
        #print('response.data: '+str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.moeda.refresh_from_db()
        self.assertEqual(self.moeda.nome, 'Bitcoin Atualizado')

    def test_delete_moeda(self):
        # Teste para excluir uma moeda
        moeda_url = reverse('moeda-detail', args=[self.moeda.id])
        response = self.client.delete(moeda_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Moeda.objects.count(), 0)
