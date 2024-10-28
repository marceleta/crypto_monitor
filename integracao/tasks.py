# integracao/tasks.py
from celery import shared_task
from datetime import date
from .historico_service import buscar_cotacoes_historicas, obter_datas_faltantes

@shared_task
def buscar_cotacoes_task(moeda_id, data_compra):
    """
    Tarefa Celery para buscar cotações em segundo plano.
    """
    from moeda.models import Moeda

    moeda = Moeda.objects.get(id=moeda_id)
    data_atual = date.today()

    # Verifica as datas faltantes
    datas_para_buscar = obter_datas_faltantes(moeda, data_compra, data_atual)

    if not datas_para_buscar:
        return "Cotações já atualizadas."

    # Busca as cotações
    buscar_cotacoes_historicas(moeda, data_compra, data_atual)
    return "Cotações atualizadas com sucesso."
