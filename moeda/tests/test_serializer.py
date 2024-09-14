from django.test import TestCase
from moeda.models import Moeda
from moeda.serializers import MoedaSerializer
from usuario.models import Usuario  # Importa o modelo de usuário

class MoedaSerializerTest(TestCase):

    def setUp(self):
        # Cria um usuário para associar à moeda
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')

        # Cria um objeto Moeda para os testes, associado ao usuário
        self.moeda = Moeda.objects.create(
            nome="Bitcoin",
            token="BTC",
            cor="#F7931A",
            logo=None,
            usuario=self.usuario  # Associando a moeda ao usuário
        )

        # Dados para teste de criação de uma nova Moeda
        self.moeda_data = {
            'nome': 'Ethereum',
            'token': 'ETH',
            'cor': '#3C3C3D',
            'logo': None,
            'usuario': self.usuario.id  # Associando ao usuário criado
        }

    def test_serializer_fields(self):
        # Testa se o serializer possui os campos corretos
        serializer = MoedaSerializer(instance=self.moeda)
        data = serializer.data
        #print(data.keys())
        self.assertEqual(set(data.keys()), set(['id', 'nome', 'token', 'cor', 'logo', 'usuario']))

    def test_serializer_serialization(self):
        # Testa se o serializer serializa corretamente os dados de um objeto Moeda
        serializer = MoedaSerializer(instance=self.moeda)
        data = serializer.data
        self.assertEqual(data['nome'], 'Bitcoin')
        self.assertEqual(data['token'], 'BTC')
        self.assertEqual(data['cor'], '#F7931A')
        self.assertIsNone(data['logo'])
        self.assertEqual(data['usuario'], self.usuario.id)  # Verificando o usuário

    def test_serializer_deserialization(self):
        # Testa se o serializer desserializa corretamente os dados e cria um novo objeto Moeda
        serializer = MoedaSerializer(data=self.moeda_data)
        self.assertTrue(serializer.is_valid())
        moeda = serializer.save()
        
        self.assertEqual(moeda.nome, 'Ethereum')
        self.assertEqual(moeda.token, 'ETH')
        self.assertEqual(moeda.cor, '#3C3C3D')
        self.assertEqual(moeda.usuario, self.usuario)  # Verificando o usuário associado

        # Verifica se o campo `logo` está vazio
        self.assertFalse(bool(moeda.logo))  # Isso verificará se não há arquivo associado ao campo logo

    def test_serializer_invalid_data(self):
        # Testa se o serializer detecta dados inválidos (token duplicado)
        Moeda.objects.create(nome="Ripple", token="XRP", cor="#00AAE4", usuario=self.usuario)
        invalid_data = {
            'nome': 'Ripple Duplicate',
            'token': 'XRP',  # Token duplicado
            'cor': '#FFFFFF',
            'logo': None,
            'usuario': self.usuario.id  # Associando ao usuário criado
        }
        serializer = MoedaSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('token', serializer.errors)  # Deve retornar erro no campo token

    def test_create_moeda(self):
        # Testa se o serializer consegue criar uma nova moeda
        serializer = MoedaSerializer(data=self.moeda_data)
        self.assertTrue(serializer.is_valid())
        moeda = serializer.save()
        self.assertEqual(Moeda.objects.count(), 2)  # Verifica se a moeda foi criada
        self.assertEqual(moeda.nome, 'Ethereum')
        self.assertEqual(moeda.token, 'ETH')

    def test_read_moeda(self):
        # Testa se o serializer consegue ler uma moeda
        serializer = MoedaSerializer(instance=self.moeda)
        data = serializer.data
        self.assertEqual(data['nome'], 'Bitcoin')
        self.assertEqual(data['token'], 'BTC')
        self.assertEqual(data['usuario'], self.usuario.id)

    def test_update_moeda(self):
        # Testa se o serializer consegue atualizar uma moeda existente
        update_data = {
            'nome': 'Bitcoin Atualizado',
            'token': 'BTC',
            'cor': '#F7931A',
            'logo': None,
            'usuario': self.usuario.id
        }
        serializer = MoedaSerializer(instance=self.moeda, data=update_data)
        self.assertTrue(serializer.is_valid())
        moeda_atualizada = serializer.save()
        self.assertEqual(moeda_atualizada.nome, 'Bitcoin Atualizado')

    def test_delete_moeda(self):
        # Testa se é possível deletar uma moeda
        moeda_id = self.moeda.id
        self.moeda.delete()
        self.assertFalse(Moeda.objects.filter(id=moeda_id).exists())  # Verifica se a moeda foi deletada

