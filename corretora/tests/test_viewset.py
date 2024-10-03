from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from usuario.models import Usuario
from corretora.models import CorretoraConfig, TipoOperacao, CorretoraUsuario


class TipoOperacaoViewSetTestCase(APITestCase):

    def setUp(self):
        # Cria tipos de operação
        self.tipo_spot = TipoOperacao.objects.create(tipo="spot")
        self.tipo_futures = TipoOperacao.objects.create(tipo="futures")

        # Cria usuário para autenticação
        self.usuario = Usuario.objects.create_user(username="usuario_teste", password="123456")
        self.client.force_authenticate(user=self.usuario)

    def test_list_tipo_operacao(self):
        # Testa a listagem dos tipos de operação
        url = reverse('tipos-operacao-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_tipo_operacao(self):
        # Testa a criação de um novo tipo de operação
        url = reverse('tipos-operacao-list')
        data = {'tipo': 'margin'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TipoOperacao.objects.count(), 3)

    def test_update_tipo_operacao(self):
        # Testa a atualização de um tipo de operação
        url = reverse('tipos-operacao-detail', args=[self.tipo_spot.id])
        data = {'tipo': 'margin'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tipo_spot.refresh_from_db()
        self.assertEqual(self.tipo_spot.tipo, 'margin')

    def test_delete_tipo_operacao(self):
        # Testa a exclusão de um tipo de operação
        url = reverse('tipos-operacao-detail', args=[self.tipo_spot.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TipoOperacao.objects.count(), 1)


class CorretoraConfigViewSetTestCase(APITestCase):

    def setUp(self):
        # Cria tipos de operação e corretora
        self.tipo_spot = TipoOperacao.objects.create(tipo="spot")
        self.tipo_futures = TipoOperacao.objects.create(tipo="futures")
        self.corretora = CorretoraConfig.objects.create(
            nome="Binance",
            url_base="https://api.binance.com",
            exige_passphrase=False
        )
        self.corretora.tipos_suportados.add(self.tipo_spot, self.tipo_futures)

        # Cria usuário para autenticação
        self.usuario = Usuario.objects.create_user(username="usuario_teste", password="123456")
        self.client.force_authenticate(user=self.usuario)

    def test_list_corretora_config(self):
        # Testa a listagem das corretoras
        url = reverse('corretoras-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_corretora_config(self):
        # Testa a criação de uma nova corretora
        url = reverse('corretoras-list')
        data = {
            'nome': 'Coinbase',
            'url_base': 'https://api.coinbase.com',
            'exige_passphrase': False,
            'tipos_suportados': [self.tipo_spot.id, self.tipo_futures.id]  # Envia uma lista de IDs para tipos_suportados
        }
        response = self.client.post(url, data)
        #print("response:", response.data)  # Verificar o que está sendo retornado no response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CorretoraConfig.objects.count(), 2)

    def test_update_corretora_config(self):
        # Testa a atualização de uma corretora
        url = reverse('corretoras-detail', args=[self.corretora.id])
        data = {'nome': 'Updated Binance', 'url_base': 'https://api.binance.com'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.corretora.refresh_from_db()
        self.assertEqual(self.corretora.nome, 'Updated Binance')

    def test_delete_corretora_config(self):
        # Testa a exclusão de uma corretora
        url = reverse('corretoras-detail', args=[self.corretora.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CorretoraConfig.objects.count(), 0)


class CorretoraUsuarioViewSetTestCase(APITestCase):

    def setUp(self):
        # Cria tipos de operação e corretora
        self.tipo_spot = TipoOperacao.objects.create(tipo="spot")
        self.tipo_futures = TipoOperacao.objects.create(tipo="futures")
        self.corretora = CorretoraConfig.objects.create(
            nome="Binance",
            url_base="https://api.binance.com",
            exige_passphrase=False
        )
        self.corretora.tipos_suportados.add(self.tipo_spot, self.tipo_futures)

        # Cria usuário e CorretoraUsuario
        self.usuario = Usuario.objects.create_user(username="usuario_teste", password="123456")
        self.corretora_usuario = CorretoraUsuario.objects.create(
            corretora=self.corretora,
            api_key="api_key",
            api_secret="api_secret",
            passphrase="passphrase",
            usuario=self.usuario
        )
        self.corretora_usuario.tipos.add(self.tipo_spot, self.tipo_futures)
        self.client.force_authenticate(user=self.usuario)

    def test_list_corretora_usuario(self):
        # Testa a listagem das corretoras associadas ao usuário
        url = reverse('corretora-usuario-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_corretora_config(self):
        # Testa a criação de uma nova corretora
        url = reverse('corretoras-list')
        data = {
            'nome': 'Coinbase',
            'url_base': 'https://api.coinbase.com',
            'exige_passphrase': False,
            'tipos_suportados': [self.tipo_spot.id, self.tipo_futures.id]  # Envia uma lista de IDs para tipos_suportados
        }
        response = self.client.post(url, data)
        #print("response:", response.data)  # Verificar o que está sendo retornado no response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CorretoraConfig.objects.count(), 2)


    def test_update_corretora_usuario(self):
        # Testa a atualização de uma corretora associada ao usuário
        url = reverse('corretora-usuario-detail', args=[self.corretora_usuario.id])
        data = {
            'api_key': 'updated_key',
            'api_secret': 'updated_secret',
            'tipos': [self.tipo_spot.id, self.tipo_futures.id],  # Inclua os tipos para garantir que são validados corretamente
            'corretora': self.corretora.id,
            'usuario': self.usuario.id
        }
        response = self.client.put(url, data)

        #
        # print("response:", response.data)  # Verificar o motivo do erro de validação
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.corretora_usuario.refresh_from_db()
        self.assertEqual(self.corretora_usuario.api_key, 'updated_key')
        self.assertEqual(self.corretora_usuario.api_secret, 'updated_secret')


    def test_delete_corretora_usuario(self):
        # Testa a exclusão de uma corretora associada ao usuário
        url = reverse('corretora-usuario-detail', args=[self.corretora_usuario.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CorretoraUsuario.objects.count(), 0)
