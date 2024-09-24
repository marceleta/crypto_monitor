from django.test import TestCase
from corretora.models import BybitCorretora
from corretora.serializers import BybitCorretoraSerializer

class BybitCorretoraSerializerTest(TestCase):

    def setUp(self):
        # Cria uma instância da corretora Bybit
        self.corretora = BybitCorretora.objects.create(
            nome="Bybit",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )

    def test_bybit_corretora_serialization(self):
        # Testa se o serializer serializa corretamente os dados de uma corretora Bybit
        serializer = BybitCorretoraSerializer(instance=self.corretora)
        data = serializer.data
        self.assertEqual(data['nome'], 'Bybit')
        # Os campos 'api_key' e 'api_secret' não devem estar presentes
        self.assertNotIn('api_key', data)
        self.assertNotIn('api_secret', data)

    def test_bybit_corretora_deserialization(self):
        # Testa se o serializer desserializa corretamente os dados e cria uma nova corretora Bybit
        data = {
            'nome': 'Bybit Test',
            # 'api_key' e 'api_secret' não são mais parte da deserialização
        }
        serializer = BybitCorretoraSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        corretora = serializer.save()
        self.assertEqual(corretora.nome, 'Bybit Test')
