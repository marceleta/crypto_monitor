
from datetime import timedelta
from integracao.factory import CorretoraServiceFactory
from moeda.models import HistoricoCotacao, Moeda
from datetime import datetime

def salvar_cotacao(moeda, data, abertura, fechamento, alta, baixa, volume):
    # Verifica se já existe uma cotação para essa moeda e data
    historico_existente = HistoricoCotacao.objects.filter(moeda=moeda, data=data).first()

    if historico_existente:
        # Atualiza os valores existentes
        historico_existente.abertura = abertura
        historico_existente.fechamento = fechamento
        historico_existente.alta = alta
        historico_existente.baixa = baixa
        historico_existente.volume = volume
        historico_existente.save()
    else:
        # Cria um novo registro de cotação
        HistoricoCotacao.objects.create(
            moeda=moeda,
            data=data,
            abertura=abertura,
            fechamento=fechamento,
            alta=alta,
            baixa=baixa,
            volume=volume
        )

def to_date(data):
    if isinstance(data, str):
        return datetime.strptime(data, '%Y-%m-%d').date()
    elif isinstance(data, datetime):
        return data.date()
    return data  # If it's already a date

def obter_datas_faltantes(moeda, data_inicial, data_final):
    # Convert both dates using the helper function
    data_inicial = to_date(data_inicial)
    data_final = to_date(data_final)

    # Obtém as datas para as quais já existem cotações
    datas_existentes = HistoricoCotacao.objects.filter(
        moeda=moeda,
        data__range=[data_inicial, data_final]
    ).values_list('data', flat=True)

    # Gera a lista completa de datas entre data_inicial e data_final
    todas_as_datas = [data_inicial + timedelta(days=i) for i in range((data_final - data_inicial).days + 1)]

    # Filtra para obter apenas as datas que ainda não estão no banco
    datas_faltantes = [data for data in todas_as_datas if data not in datas_existentes]

    return datas_faltantes



def buscar_cotacoes_historicas(moeda, data_compra, data_atual, intervalo='1M'):
    """
    Busca cotações históricas para uma moeda no intervalo entre data_compra e data_atual.
    O intervalo padrão é mensal ('1M'), mas pode ser configurado para diário ('1D'), semanal ('1W'), etc.
    """

    # Converte as datas para datetime.date
    data_compra = to_date(data_compra)
    data_atual = to_date(data_atual)

    # Instancia o serviço de integração com a corretora
    servico = CorretoraServiceFactory.criar_servico(moeda.corretora)

    # Faz a requisição para obter as cotações com o intervalo especificado
    cotacoes = servico.buscar_cotacoes_por_intervalo(moeda.token, data_compra, data_atual, intervalo=intervalo)
    # Itera sobre as cotações recebidas e salva no banco
    for cotacao in cotacoes:
        data = cotacao['data']  # Certifique-se de que a API retorna a data de cada registro
        salvar_cotacao(
            moeda=moeda,
            data=data,
            abertura=cotacao['abertura'],
            fechamento=cotacao['fechamento'],
            alta=cotacao['alta'],
            baixa=cotacao['baixa'],
            volume=cotacao['volume']
        )

