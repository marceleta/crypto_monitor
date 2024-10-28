from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
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
        # Cria tipos de operação e corretoras
        self.tipo_spot = TipoOperacao.objects.create(tipo="spot")
        self.tipo_futures = TipoOperacao.objects.create(tipo="futures")
        
        # Cria corretoras
        self.corretora_binance = CorretoraConfig.objects.create(
            nome="Binance",
            url_base="https://api.binance.com",
            exige_passphrase=False
        )
        self.corretora_coinbase = CorretoraConfig.objects.create(
            nome="Coinbase",
            url_base="https://api.coinbase.com",
            exige_passphrase=False
        )
        self.corretora_binance.tipos_suportados.add(self.tipo_spot, self.tipo_futures)
        self.corretora_coinbase.tipos_suportados.add(self.tipo_spot)

        # Cria usuário e corretora associada
        self.usuario = Usuario.objects.create_user(username="usuario_teste", password="123456")
        self.corretora_usuario_binance = CorretoraUsuario.objects.create(
            corretora=self.corretora_binance,
            api_key="api_key_binance",
            api_secret="api_secret_binance",
            passphrase=None,
            usuario=self.usuario
        )
        self.corretora_usuario_coinbase = CorretoraUsuario.objects.create(
            corretora=self.corretora_coinbase,
            api_key="api_key_coinbase",
            api_secret="api_secret_coinbase",
            passphrase=None,
            usuario=self.usuario
        )
        self.client.force_authenticate(user=self.usuario)

    def test_list_corretora_usuario(self):
        # Testa a listagem das corretoras associadas ao usuário
        url = reverse('corretora-usuario-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Ajustado para refletir 2 corretoras criadas

    def test_create_corretora_usuario(self):
        # Testa a criação de uma nova corretora associada ao usuário
        url = reverse('corretora-usuario-list')
        data = {
            'corretora': self.corretora_binance.id,  # Usa a corretora criada no setUp
            'api_key': 'new_api_key',
            'api_secret': 'new_api_secret',
            'passphrase': 'new_passphrase',
            'tipos': [self.tipo_spot.id],  # Passa os IDs dos tipos de operação
            'usuario': self.usuario.id  # Passa o ID do usuário autenticado
        }
        response = self.client.post(url, data)
        
        # Verifica se a resposta é 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verifica se o objeto foi criado corretamente no banco de dados
        corretora_usuario = CorretoraUsuario.objects.get(api_key='new_api_key')
        self.assertEqual(corretora_usuario.api_secret, 'new_api_secret')
        self.assertEqual(corretora_usuario.passphrase, 'new_passphrase')
        self.assertEqual(corretora_usuario.corretora.id, self.corretora_binance.id)
        self.assertTrue(corretora_usuario.tipos.filter(id=self.tipo_spot.id).exists())

    def test_create_corretora_usuario_without_passphrase(self):
        # Testa a criação de uma corretora associada ao usuário sem passphrase
        url = reverse('corretora-usuario-list')
        data = {
            'corretora': self.corretora_binance.id,  # Usa a corretora do setUp
            'api_key': 'new_api_key',
            'api_secret': 'new_api_secret',
            'tipos': [self.tipo_spot.id],
            'usuario': self.usuario.id,
            'passphrase': ''  # Não inclui passphrase
        }

        response = self.client.post(url, data)
        
        # Verifica se a resposta é 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verifica se o objeto foi criado corretamente no banco de dados
        corretora_usuario = CorretoraUsuario.objects.get(api_key='new_api_key')
        self.assertEqual(corretora_usuario.api_secret, 'new_api_secret')
        self.assertIsNone(corretora_usuario.passphrase)  # Passphrase deve ser None
        self.assertEqual(corretora_usuario.corretora.id, self.corretora_binance.id)

    def test_update_corretora_usuario(self):
        # Testa a atualização de uma corretora associada ao usuário
        url = reverse('corretora-usuario-detail', args=[self.corretora_usuario_binance.id])
        data = {
            'api_key': 'updated_key',
            'api_secret': 'updated_secret',
            'tipos': [self.tipo_spot.id, self.tipo_futures.id],
            'corretora': self.corretora_binance.id,
            'usuario': self.usuario.id
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.corretora_usuario_binance.refresh_from_db()
        self.assertEqual(self.corretora_usuario_binance.api_key, 'updated_key')
        self.assertEqual(self.corretora_usuario_binance.api_secret, 'updated_secret')

    def test_delete_corretora_usuario(self):
        # Testa a exclusão de uma corretora associada ao usuário
        url = reverse('corretora-usuario-detail', args=[self.corretora_usuario_binance.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CorretoraUsuario.objects.count(), 1)

    def test_buscar_corretora_por_nome(self):
        # Testa a action personalizada que busca corretoras associadas ao usuário pelo nome
        url = reverse('corretora-usuario-buscar-por-nome')

        # Faz a requisição passando o nome parcial "Binance"
        response = self.client.get(url, {'nome': 'Binance'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['corretora'], self.corretora_binance.id)  # Ajustado para lidar com o ID

        # Faz a requisição passando o nome parcial "Coinbase"
        response = self.client.get(url, {'nome': 'Coinbase'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['corretora'], self.corretora_coinbase.id)

    def test_buscar_corretora_por_nome_sem_parametro(self):
        # Testa a action sem passar o nome da corretora
        url = reverse('corretora-usuario-buscar-por-nome')

        # Faz a requisição sem passar o parâmetro "nome"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Nome do corretor não fornecido.')

    def test_buscar_corretoras_do_usuario(self):
        # Testa a listagem das corretoras associadas ao usuário autenticado
        url = reverse('corretora-usuario-list')  # Endereço da rota que lista as corretoras do usuário
        response = self.client.get(url)
        #print('test_buscar_corretoras_do_usuario response.data: '+str(response.data))
        # Verifica se a resposta é HTTP 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se foram retornadas 2 corretoras (criadas no setup)
        self.assertEqual(len(response.data), 2)

        # Verifica os detalhes da primeira corretora
        corretora_binance_data = response.data[0]
        self.assertEqual(corretora_binance_data['corretora'], self.corretora_binance.id)
        

        # Verifica os detalhes da segunda corretora
        corretora_coinbase_data = response.data[1]
        self.assertEqual(corretora_coinbase_data['corretora'], self.corretora_coinbase.id)


class CorretoraUsuarioDetailViewSetTest(APITestCase):

    def setUp(self):
        # Configuração inicial para os testes
        self.usuario = Usuario.objects.create_user(username='testuser', password='12345')
        self.usuario_outro = Usuario.objects.create_user(username='otheruser', password='12345')

        # Criação dos Tipos de Operação
        self.tipo_spot = TipoOperacao.objects.create(tipo='spot')
        self.tipo_futures = TipoOperacao.objects.create(tipo='futures')

        # Criação de CorretoraConfig
        self.corretora_config = CorretoraConfig.objects.create(
            nome="Bybit",
            url_base="https://api.bybit.com",
            exige_passphrase=True
        )

        # Adiciona os tipos suportados à CorretoraConfig
        self.corretora_config.tipos_suportados.add(self.tipo_spot, self.tipo_futures)

        # Criação de CorretoraUsuario para o usuário autenticado
        self.corretora_usuario = CorretoraUsuario.objects.create(
            usuario=self.usuario,
            corretora=self.corretora_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            passphrase="test_passphrase"
        )
        # Adiciona os tipos à CorretoraUsuario
        self.corretora_usuario.tipos.add(self.tipo_spot, self.tipo_futures)

        # Criação de CorretoraUsuario para outro usuário (não deve ser acessível)
        self.corretora_usuario_outro = CorretoraUsuario.objects.create(
            usuario=self.usuario_outro,
            corretora=self.corretora_config,
            api_key="other_api_key",
            api_secret="other_api_secret",
            passphrase="other_passphrase"
        )
        # Adiciona os tipos à CorretoraUsuario de outro usuário
        self.corretora_usuario_outro.tipos.add(self.tipo_spot)

        self.client = APIClient()
        self.url_detail = reverse('corretora-usuario-detalhes-detail', kwargs={'pk': self.corretora_usuario.pk})
        self.url_list = reverse('corretora-usuario-detalhes-list')


    def test_list_corretora_usuario_autenticado(self):
        """
        Testa se o usuário autenticado pode listar apenas suas próprias corretoras.
        """
        # Autentica o cliente com o usuário
        self.client.force_authenticate(user=self.usuario)

        # Faz a requisição GET para listar as corretoras do usuário
        response = self.client.get(self.url_list)
        #print('test_list_corretora_usuario_autenticado: response.data: '+str(response.data))
        # Verifica se a resposta tem status 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verifica se a lista contém apenas a corretora do usuário autenticado
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['usuario'], self.usuario.id)
        self.assertEqual(response.data[0]['corretora']['nome'], 'Bybit')

    def test_retrieve_corretora_usuario_autenticado(self):
        """
        Testa se o usuário autenticado pode recuperar os detalhes de sua própria corretora.
        """
        # Autentica o cliente com o usuário
        self.client.force_authenticate(user=self.usuario)

        # Faz a requisição GET para recuperar a corretora do usuário
        response = self.client.get(self.url_detail)

        # Verifica se a resposta tem status 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verifica se os dados retornados são os corretos
        self.assertEqual(response.data['usuario'], self.usuario.id)
        self.assertEqual(response.data['corretora']['nome'], 'Bybit')

    def test_retrieve_corretora_usuario_nao_autenticado(self):
        """
        Testa se o usuário não autenticado não pode recuperar os detalhes de uma corretora.
        """
        # Faz a requisição GET sem autenticação
        response = self.client.get(self.url_detail)

        # Verifica se a resposta tem status 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_corretora_usuario_de_outro_usuario(self):
        """
        Testa se um usuário autenticado não pode acessar os detalhes de outra corretora.
        """
        # Autentica o cliente com outro usuário
        self.client.force_authenticate(user=self.usuario_outro)

        # Faz a requisição GET para recuperar a corretora que pertence a outro usuário
        response = self.client.get(self.url_detail)

        # Verifica se a resposta tem status 404 (Not Found)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_corretora_usuario_nao_autenticado(self):
        """
        Testa se o usuário não autenticado não pode listar as corretoras.
        """
        # Faz a requisição GET sem autenticação
        response = self.client.get(self.url_list)

        # Verifica se a resposta tem status 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_corretora_usuario_de_outro_usuario(self):
        """
        Testa se um usuário autenticado não pode ver as corretoras de outros usuários.
        """
        # Autentica o cliente com outro usuário
        self.client.force_authenticate(user=self.usuario_outro)

        # Faz a requisição GET para listar as corretoras do usuário autenticado
        response = self.client.get(self.url_list)

        # Verifica se a lista está vazia
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['usuario'], self.usuario_outro.id)
        self.assertEqual(response.data[0]['corretora']['nome'], 'Bybit')







        


