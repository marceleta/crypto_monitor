from rest_framework import viewsets, status
from rest_framework.viewsets import GenericViewSet
from ativo.models import Ativo
from moeda.models import Moeda, HistoricoCotacao
from moeda.serializers import HistoricoCotacaoSerializer
from rest_framework.permissions import IsAuthenticated  # Certifique-se de que a autenticação é obrigatória
from rest_framework.response import Response
from rest_framework.decorators import action
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from django.db.models.functions import TruncWeek, TruncMonth, Floor, ExtractDay, TruncYear
from django.db.models import Avg, ExpressionWrapper, IntegerField, F, Max, Min
from rest_framework.pagination import PageNumberPagination



class DashboardViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing HistoricoCotacao instances.
    """
    queryset = HistoricoCotacao.objects.all()  # Definimos o queryset com todos os registros
    serializer_class = HistoricoCotacaoSerializer  # Usamos o serializer que já foi criado
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def grafico_distribuicao_ativos(self, request):
        user = request.user  # Obter o usuário autenticado

        # Passo 1: Recuperar os ativos comprados pelo usuário
        ativos = Ativo.objects.filter(usuario=user)

        # Dicionário para agrupar ativos por moeda
        ativos_agrupados = defaultdict(lambda: {'quantidade_total': 0, 'valor_total_compra': 0})

        # Passo 2: Para cada ativo, agrupar por moeda e somar as quantidades
        for ativo in ativos:
            moeda = ativo.moeda
            ativos_agrupados[moeda]['quantidade_total'] += ativo.quantidade
            ativos_agrupados[moeda]['valor_total_compra'] += ativo.valor_compra

        distribuicao = []
        valor_total_carteira = 0

        # Passo 3: Calcular o valor total de cada ativo com base na última cotação
        for moeda, dados in ativos_agrupados.items():
            # Buscar a última cotação da moeda
            cotacao_atual = HistoricoCotacao.objects.filter(moeda=moeda).order_by('-data').first()

            if cotacao_atual:
                valor_atual = cotacao_atual.preco
                quantidade_total = dados['quantidade_total']
                valor_total = valor_atual * quantidade_total
                valor_total_carteira += valor_total

                distribuicao.append({
                    'moeda': moeda.nome,
                    'valor_total': valor_total,
                    'quantidade_total': quantidade_total
                })

        # Passo 4: Calcular a distribuição percentual com base no valor total da carteira
        for ativo in distribuicao:
            ativo['percentual'] = (ativo['valor_total'] / valor_total_carteira) * 100

        # Passo 5: Retornar os dados formatados para o frontend
        return Response({
            'valor_total_carteira': valor_total_carteira,
            'distribuicao': distribuicao
        })

class AtivoDetalheViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def historico_preco(self, request, pk=None):
        """
        Este endpoint retorna o histórico de preços para um ativo específico (moeda),
        agrupado por semana, quinzena ou mês. O usuário pode especificar o agrupamento
        e um intervalo de datas.
        """
        try:
            # Obter o usuário autenticado
            user = request.user

            # Recuperar a moeda que pertence ao usuário autenticado
            moeda = Moeda.objects.get(pk=pk, usuario=user)

            # Definir o tipo de agrupamento (mensal por padrão)
            agrupamento = request.query_params.get('agrupamento', 'mensal')

            # Validar o agrupamento
            if agrupamento not in ['semanal', 'quinzenal', 'mensal']:
                return Response({"error": "Agrupamento inválido. Use 'semanal', 'quinzenal' ou 'mensal'."}, status=400)

            # Definir o período (se enviado pelo usuário)
            data_inicio_str = request.query_params.get('data_inicio')
            data_fim_str = request.query_params.get('data_fim')

            # Filtrar cotações por período, se especificado
            if data_inicio_str and data_fim_str:
                # Converter strings para objetos date
                try:
                    data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
                    data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response({"error": "Formato de data inválido. Use AAAA-MM-DD."}, status=400)
                
                historico_cotacoes = HistoricoCotacao.objects.filter(
                    moeda=moeda,
                    data__range=[data_inicio, data_fim]
                )
            else:
                # Se não houver filtro de período, retorna todas as cotações
                historico_cotacoes = HistoricoCotacao.objects.filter(moeda=moeda)

            # **Aqui está o ajuste de indentação**
            # Agrupar os dados conforme o tipo de agrupamento
            if agrupamento == 'semanal':
                historico_agrupado = historico_cotacoes.annotate(
                    periodo=TruncWeek('data')
                ).values('periodo').annotate(
                    preco_medio=Avg('preco')
                ).order_by('periodo')

            elif agrupamento == 'quinzenal':
                # Calcular a quinzena com base no dia do mês
                historico_agrupado = historico_cotacoes.annotate(
                    dia=ExtractDay('data'),
                    quinzena=ExpressionWrapper(
                        Floor((F('dia') - 1) / 15) + 1,
                        output_field=IntegerField()
                    ),
                    mes=TruncMonth('data')
                ).values('mes', 'quinzena').annotate(
                    preco_medio=Avg('preco')
                ).order_by('mes', 'quinzena')

            else:  # Agrupamento mensal
                historico_agrupado = historico_cotacoes.annotate(
                    periodo=TruncMonth('data')
                ).values('periodo').annotate(
                    preco_medio=Avg('preco')
                ).order_by('periodo')

            # Formatar a resposta
            historico = []
            if agrupamento == 'quinzenal':
                for cotacao in historico_agrupado:
                    historico.append({
                        'mes': cotacao['mes'],
                        'quinzena': cotacao['quinzena'],
                        'preco': cotacao['preco_medio']
                    })
            else:
                for cotacao in historico_agrupado:
                    historico.append({
                        'data': cotacao['periodo'],
                        'preco': cotacao['preco_medio']
                    })

            return Response({
                'moeda': moeda.nome,
                'historico': historico
            })

        except Moeda.DoesNotExist:
            return Response({"error": "Moeda não encontrada para o usuário"}, status=404)

class PatrimonioEvolucaoPagination(PageNumberPagination):
    page_size = 12
    page_size_param  = 'page_size'
    max_page_size = 100

class PatrimonioEvolucaoViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = PatrimonioEvolucaoPagination

    @action(detail=False, methods=['get'])
    def evolucao_patrimonio(self, request):
        user = request.user

        moedas = Moeda.objects.filter(usuario=user)
        #Verifica se o usuário possui moedas
        if not moedas.exists():
            return Response({'error':'O usuário não possui ativos'}, status=status.HTTP_404_NOT_FOUND)


        patrimonio = {}
        soma_periodo = {}

        for moeda in moedas:
            ativos = Ativo.objects.filter(usuario=user, moeda=moeda)
            # Se o usuário não possuir ativos, retornar um erro
            if not ativos.exists():
                return Response({"error": "O usuário não possui ativos"}, status=status.HTTP_404_NOT_FOUND)

            patrimonio[moeda.nome] = {
                'token': moeda.token,
                'ativos': {}
            }

            for ativo in ativos:
                #print('Ativo: ' + str(ativo))

                data_compra = ativo.data_compra
                historio = HistoricoCotacao.objects.filter(data=data_compra).first()

                valor_ativo = ativo.quantidade * historio.preco
                #print('Valor_ativo: ' + str(valor_ativo))

                patrimonio[moeda.nome]['ativos'][str(ativo)] = {
                    'cotacoes': []
                }

                # Definir o tipo de agrupamento (mensal por padrão ou anual)
                agrupamento = request.query_params.get('agrupamento', 'mensal')

                if agrupamento == 'mensal':
                    cotacoes = HistoricoCotacao.objects.filter(moeda=moeda, data__gte=ativo.data_compra).annotate(
                        mes=TruncMonth('data')  # Agrupa por mês
                    ).values('mes').annotate(
                        ultimo_dia=Max('data')  # Pega a última data de cada mês
                    ).order_by('-mes', 'ultimo_dia')

                elif agrupamento == 'anual':
                    cotacoes = HistoricoCotacao.objects.filter(moeda=moeda, data__gte=ativo.data_compra).annotate(
                        ano=TruncYear('data')  # Agrupa por ano
                    ).values('ano').annotate(
                        ultimo_dia=Max('data')  # Pega a última data de cada ano
                    ).order_by('-ano', 'ultimo_dia')

                else:
                    return Response({"error": "Agrupamento inválido."}, status=400)

                for cotacao in cotacoes:
                    if agrupamento == 'mensal':
                        periodo = cotacao['mes'].strftime('%B %Y')
                    elif agrupamento == 'anual':
                        periodo = cotacao['ano'].strftime('%Y')

                    cotacao_ultimo_dia = HistoricoCotacao.objects.filter(
                        moeda=moeda, data=cotacao['ultimo_dia']).first()

                    cotacao_no_periodo = ativo.quantidade * Decimal(cotacao_ultimo_dia.preco)
                    cotacao_ativo = cotacao_no_periodo - valor_ativo

                    patrimonio[moeda.nome]['ativos'][str(ativo)]['cotacoes'].append({
                        'periodo': periodo,
                        'evolucao_preco_ativo': cotacao_ativo
                    })

                    # Acumular a soma anual ou mensal
                    if periodo in soma_periodo:
                        soma_periodo[periodo] += cotacao_ativo
                    else:
                        soma_periodo[periodo] = cotacao_ativo

            
        soma_periodo_list = [ {'periodo': periodo, 'valor': str(valor)} for periodo, valor in soma_periodo.items()]
        paginated_response = self.paginate_queryset(soma_periodo_list)

        if paginated_response is not None:
            return self.get_paginated_response(paginated_response)

        return Response({
            'soma_periodo':soma_periodo_list
        })










