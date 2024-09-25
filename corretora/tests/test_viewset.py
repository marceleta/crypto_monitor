from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from usuario.models import Usuario
from corretora.models import Corretora
from moeda.models import Moeda, HistoricoCotacao
from unittest.mock import patch

class CorretoraViewSetTest(APITestCase):

    def setUp(self):
        # Criar um usuário para autenticação
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.usuario)

        # Dados para a criação de uma corretora
        self.corretora_data = {
            'nome': 'Test Corretora',
            'url_base': 'https://api.testcorretora.com',
            'api_key': 'test_api_key',
            'api_secret': 'test_api_secret',
            'passphrase': 'test_passphrase',
            'tipo': 'spot'
        }

        # Criar uma corretora associada ao usuário
        self.corretora = Corretora.objects.create(usuario=self.usuario, **self.corretora_data)

        # Criar uma moeda para os testes
        self.moeda = Moeda.objects.create(nome='BTCUSD')

        # URL para o ViewSet
        self.url_list = reverse('corretora-list')
        self.url_detail = reverse('corretora-detail', args=[self.corretora.id])
        # URL para o endpoint buscar_preco_ativo
        self.url_buscar_preco_ativo = reverse('corretora-buscar-preco-ativo', args=[self.corretora.id])


    def test_list_corretoras(self):
        """Teste para listar corretoras do usuário autenticado"""
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Deve retornar 1 corretora
        self.assertEqual(response.data[0]['nome'], 'Test Corretora')

    def test_create_corretora(self):
        """Teste para criar uma nova corretora"""
        new_corretora_data = {
            'nome': 'Nova Corretora',
            'url_base': 'https://api.novacorretora.com',
            'api_key': 'nova_api_key',
            'api_secret': 'nova_api_secret',
            'passphrase': 'nova_passphrase',
            'tipo': 'futures'
        }
        response = self.client.post(self.url_list, new_corretora_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Corretora.objects.count(), 2)  # Deve ter duas corretoras agora
        self.assertEqual(response.data['nome'], 'Nova Corretora')

    def test_update_corretora(self):
        """Teste para atualizar uma corretora existente"""
        updated_data = {
            'nome': 'Corretora Atualizada',
            'url_base': 'https://api.atualizadacorretora.com',
            'tipo': 'futures'
        }
        response = self.client.put(self.url_detail, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.corretora.refresh_from_db()  # Atualizar a instância da corretora do banco de dados
        self.assertEqual(self.corretora.nome, 'Corretora Atualizada')
        self.assertEqual(self.corretora.url_base, 'https://api.atualizadacorretora.com')
        self.assertEqual(self.corretora.tipo, 'futures')

    def test_partial_update_corretora(self):
        """Teste para atualizar parcialmente uma corretora (PATCH)"""
        partial_update_data = {'nome': 'Corretora Parcialmente Atualizada'}
        response = self.client.patch(self.url_detail, partial_update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.corretora.refresh_from_db()
        self.assertEqual(self.corretora.nome, 'Corretora Parcialmente Atualizada')

    def test_delete_corretora(self):
        """Teste para deletar uma corretora"""
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Corretora.objects.count(), 0)  # Deve não haver mais corretoras

    def test_teste_conexao(self):
        """Teste para o endpoint customizado 'teste_conexao'"""
        url_teste_conexao = reverse('corretora-teste-conexao', args=[self.corretora.id])
        response = self.client.get(url_teste_conexao)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Conexão OK')

    def test_unauthenticated_access(self):
        """Teste para garantir que não-autenticados não possam acessar o ViewSet"""
        self.client.logout()  # Desautenticar o cliente
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



    @patch('corretora.services.BybitService.buscar_preco_ativo')
    def test_buscar_preco_ativo_sucesso(self, mock_buscar_preco_ativo):
        """
        Teste para verificar o sucesso da busca de preço de um ativo e salvamento no banco de dados.
        """
        # Simular o retorno da API de buscar preço do ativo
        mock_buscar_preco_ativo.return_value = {
            'abertura': '45000.0',
            'fechamento': '45500.0',
            'alta': '46000.0',
            'baixa': '44000.0',
            'volume': '100.0',
            'data': '2023-09-01'
        }

        # Fazer a requisição POST com os dados do ativo e da data
        data = {
            'ativo': 'BTCUSD',
            'data': '2023-09-01'
        }
        response = self.client.post(self.url_buscar_preco_ativo, data, format='json')

        # Verificar se a resposta foi bem-sucedida
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar se os dados foram salvos no banco de dados corretamente
        historico = HistoricoCotacao.objects.get(moeda=self.moeda, data='2023-09-01')
        self.assertEqual(historico.preco, 45500.0)  # Preço de fechamento salvo corretamente

    def test_buscar_preco_ativo_falta_dados(self):
        """
        Teste para verificar a resposta quando os dados obrigatórios não são fornecidos.
        """
        data = {
            'ativo': '',
            'data': ''
        }
        response = self.client.post(self.url_buscar_preco_ativo, data, format='json')

        # Verificar se o status de resposta é 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('erro', response.data)

    def test_buscar_preco_ativo_moeda_nao_encontrada(self):
        """
        Teste para verificar a resposta quando a moeda não é encontrada.
        """
        data = {
            'ativo': 'ETHUSD',  # Moeda não cadastrada no sistema
            'data': '2023-09-01'
        }
        response = self.client.post(self.url_buscar_preco_ativo, data, format='json')

        # Verificar se o status de resposta é 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('erro', response.data)
