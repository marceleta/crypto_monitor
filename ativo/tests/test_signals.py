from django.test import TestCase
from unittest.mock import patch
from ativo.models import Ativo
from moeda.models import Moeda
from usuario.models import Usuario
from datetime import date

from django.db.models.signals import post_save
from ativo.signals import iniciar_busca_apos_criacao_ativo

class TestIniciarBuscaAposCriacaoAtivo(TestCase):

    @classmethod
    def setUpTestData(cls):

        # Conectar o sinal explicitamente
        post_save.connect(iniciar_busca_apos_criacao_ativo, sender=Ativo)
        
        # Cria um usuário e uma moeda para usar nos testes
        cls.usuario = Usuario.objects.create_user(username='testuser', password='12345')
        cls.moeda = Moeda.objects.create(nome='Bitcoin', token='BTC', usuario=cls.usuario)

    @patch('integracao.tasks.buscar_cotacoes_task.delay')
    def test_iniciar_busca_apos_criacao_ativo(self, mock_buscar_cotacoes_task):
        # Cria um ativo, o que deve disparar o sinal
        Ativo.objects.create(
            moeda=self.moeda,
            valor_compra=40.000,
            data_compra=date(2023, 10, 1),
            quantidade=1.0,
            usuario=self.usuario
        )

        # Verifica se a tarefa Celery foi chamada
        mock_buscar_cotacoes_task.assert_called_once_with(self.moeda.id, date(2023, 10, 1))
