from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch, MagicMock
from moeda.models import HistoricoCotacao, Moeda
from datetime import date
from integracao.historico_service import salvar_cotacao, obter_datas_faltantes, buscar_cotacoes_historicas
from usuario.models import Usuario
from corretora.models import CorretoraConfig, CorretoraUsuario, TipoOperacao



class HistoricoServiceTestCase(TestCase):

    def setUp(self):
        # Criação do usuário para associar à moeda e à corretora
        self.usuario = Usuario.objects.create_user(username='testuser', password='12345')

        # Criação de uma instância de CorretoraConfig
        self.corretora_config = CorretoraConfig.objects.create(
            nome="Bybit",
            url_base="https://api.bybit.com",
            exige_passphrase=True
        )

        # Criação de tipos de operação
        self.tipo_spot = TipoOperacao.objects.create(tipo='spot')
        self.tipo_futures = TipoOperacao.objects.create(tipo='futures')

        # Associa os tipos de operação à corretora
        self.corretora_config.tipos_suportados.add(self.tipo_spot, self.tipo_futures)

        # Criação de uma instância de CorretoraUsuario
        self.corretora_usuario = CorretoraUsuario.objects.create(
            corretora=self.corretora_config,
            api_key="test_api_key",
            api_secret="test_api_secret",
            passphrase="test_passphrase",
            usuario=self.usuario
        )
        # Associa os tipos de operação à CorretoraUsuario
        self.corretora_usuario.tipos.add(self.tipo_spot, self.tipo_futures)

        # Criação de uma instância de Moeda associada à corretora
        self.moeda = Moeda.objects.create(
            nome='Bitcoin',
            token='BTC',
            usuario=self.usuario,
            corretora_content_type=ContentType.objects.get_for_model(CorretoraUsuario),
            corretora_object_id=self.corretora_usuario.id
        )

        # Definição das datas para o teste
        self.data_compra = date(2024, 3, 1)
        self.data_atual = date(2024, 10, 22)

    def test_salvar_cotacao_nova(self):
        # Testa a criação de uma nova cotação
        salvar_cotacao(
            moeda=self.moeda,
            data=self.data_compra,
            abertura=40000,
            fechamento=40500,
            alta=41000,
            baixa=39500,
            volume=1200
        )

        # Verifica se a cotação foi salva corretamente
        historico = HistoricoCotacao.objects.get(moeda=self.moeda, data=self.data_compra)
        self.assertEqual(historico.abertura, 40000)
        self.assertEqual(historico.fechamento, 40500)
        self.assertEqual(historico.alta, 41000)
        self.assertEqual(historico.baixa, 39500)
        self.assertEqual(historico.volume, 1200)

    def test_salvar_cotacao_existente(self):
        # Cria uma cotação existente
        HistoricoCotacao.objects.create(
            moeda=self.moeda,
            data=self.data_compra,
            abertura=39000,
            fechamento=39500,
            alta=40000,
            baixa=38500,
            volume=1000
        )

        # Atualiza a cotação existente
        salvar_cotacao(
            moeda=self.moeda,
            data=self.data_compra,
            abertura=40000,
            fechamento=40500,
            alta=41000,
            baixa=39500,
            volume=1200
        )

        # Verifica se a cotação foi atualizada
        historico = HistoricoCotacao.objects.get(moeda=self.moeda, data=self.data_compra)
        self.assertEqual(historico.abertura, 40000)
        self.assertEqual(historico.fechamento, 40500)
        self.assertEqual(historico.alta, 41000)
        self.assertEqual(historico.baixa, 39500)
        self.assertEqual(historico.volume, 1200)

    def test_obter_datas_faltantes(self):
        # Cria uma cotação existente no intervalo
        HistoricoCotacao.objects.create(
            moeda=self.moeda,
            data=date(2024, 3, 5),
            abertura=39000,
            fechamento=39500,
            alta=40000,
            baixa=38500,
            volume=1000
        )

        # Testa obter datas faltantes entre a data de compra e a data atual
        datas_faltantes = obter_datas_faltantes(self.moeda, self.data_compra, self.data_atual)
        

        # Verifica se a lista de datas faltantes não inclui a data com cotação existente
        self.assertNotIn(date(2024, 3, 5), datas_faltantes)

        # Verifica se outras datas estão presentes na lista
        self.assertIn(date(2024, 3, 1), datas_faltantes)
        self.assertIn(date(2024, 3, 2), datas_faltantes)

    @patch('integracao.services.BybitService.buscar_cotacoes_por_intervalo')
    def test_buscar_cotacoes_historicas(self, mock_buscar_cotacoes_por_intervalo):
        # Mocka a resposta do método buscar_cotacoes_por_intervalo para retornar dados de cotações
        mock_buscar_cotacoes_por_intervalo.return_value = [
            {
                'abertura': 40000,
                'fechamento': 40500,
                'alta': 41000,
                'baixa': 39500,
                'volume': 1200,
                'data': '2024-03-01'
            },
            {
                'abertura': 40500,
                'fechamento': 41000,
                'alta': 41500,
                'baixa': 40000,
                'volume': 1300,
                'data': '2024-03-02'
            },
            {
                'abertura': 41000,
                'fechamento': 41500,
                'alta': 42000,
                'baixa': 40500,
                'volume': 1400,
                'data': '2024-03-03'
            }
        ]

        # Executa a função para buscar cotações históricas
        buscar_cotacoes_historicas(self.moeda, self.data_compra, self.data_atual)

        # Verifica se o serviço de integração foi chamado para o intervalo fornecido
        mock_buscar_cotacoes_por_intervalo.assert_called_once_with(
            'BTC',
            self.data_compra,
            self.data_atual,
            intervalo='1M'
        )

        # Verifica se as cotações foram salvas no banco de dados
        self.assertEqual(HistoricoCotacao.objects.count(), 3)

        # Verifica os valores salvos para a primeira cotação
        historico = HistoricoCotacao.objects.get(moeda=self.moeda, data=date(2024, 3, 1))
        self.assertEqual(historico.abertura, 40000)
        self.assertEqual(historico.fechamento, 40500)
        self.assertEqual(historico.alta, 41000)
        self.assertEqual(historico.baixa, 39500)
        self.assertEqual(historico.volume, 1200)

