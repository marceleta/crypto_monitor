from django.test import TestCase
from ativo.models import Ativo
from moeda.models import Moeda
from usuario.models import Usuario
from ativo.serializers import AtivoSerializer
from django.db.models.signals import post_save
from ativo.signals import iniciar_busca_apos_criacao_ativo

class AtivoSerializerTest(TestCase):

    def setUp(self):
        # Cria um usuário para associar aos ativos
        self.usuario = Usuario.objects.create_user(username='testuser', password='testpass')
        post_save.disconnect(iniciar_busca_apos_criacao_ativo, sender=Ativo)

        # Cria uma moeda para associar aos ativos
        self.moeda = Moeda.objects.create(
            nome="Bitcoin",
            token="BTC",
            cor="#F7931A",
            logo=None,
            usuario=self.usuario
        )

        # Cria um ativo para os testes
        self.ativo = Ativo.objects.create(
            moeda=self.moeda,
            data_compra="2024-09-12",
            valor_compra=10000.00,
            usuario=self.usuario,
            quantidade=0.5,
        )

        # Dados para criação de um novo ativo
        self.ativo_data = {
            'moeda_id': self.moeda.id,
            'data_compra': '2024-09-11',
            'valor_compra': 5000.00
        }

    def test_serializer_fields(self):
        # Testa se o serializer possui os campos corretos
        serializer = AtivoSerializer(instance=self.ativo)
        data = serializer.data
        #print("test_serializer_serialization: data: "+str(data))
        expected_fields = {'id', 'moeda', 'data_compra', 'valor_compra', 'usuario'}
        self.assertEqual(set(data.keys()), expected_fields)

    def test_serializer_serialization(self):
        # Testa se o serializer serializa corretamente os dados de um objeto Ativo
        serializer = AtivoSerializer(instance=self.ativo)
        data = serializer.data
        #print("test_serializer_serialization: data: "+str(data))
        self.assertEqual(data['moeda']['id'], self.moeda.id)
        self.assertEqual(data['valor_compra'], '10000.00')
        self.assertEqual(data['data_compra'], '2024-09-12')
        self.assertEqual(data['usuario'], self.usuario.id)

    def test_serializer_deserialization(self):
        # Testa se o serializer desserializa corretamente os dados e cria um novo objeto Ativo
        serializer = AtivoSerializer(data=self.ativo_data)
        
        if not serializer.is_valid():
            print('test_serializer_deserialization serializer: '+str(serializer.errors))

        self.assertTrue(serializer.is_valid())
        
        ativo = serializer.save(usuario=self.usuario)
        self.assertEqual(ativo.moeda, self.moeda)
        self.assertEqual(ativo.valor_compra, 5000.00)
        self.assertEqual(str(ativo.data_compra), '2024-09-11')
        self.assertEqual(ativo.usuario, self.usuario)

    def test_serializer_update(self):
        # Testa se o serializer atualiza corretamente um objeto Ativo
        data = {
            'moeda_id': self.moeda.id,
            'data_compra': '2024-09-15',
            'valor_compra': 12000.00,
            'usuario': self.usuario
        }
        serializer = AtivoSerializer(instance=self.ativo, data=data, partial=True)
        
        self.assertTrue(serializer.is_valid())
        ativo_atualizado = serializer.save()
        self.assertEqual(ativo_atualizado.valor_compra, 12000.00)
        self.assertEqual(str(ativo_atualizado.data_compra), '2024-09-15')

    def test_serializer_invalid_data(self):
        # Testa se o serializer detecta dados inválidos
        invalid_data = {
            'moeda_id': None,  # Moeda não pode ser None
            'data_compra': '2024-09-11',
            'valor_compra': 5000.00
        }
        serializer = AtivoSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('moeda_id', serializer.errors)
