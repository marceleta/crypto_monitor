
from django.db.models.signals import post_save
from django.dispatch import receiver
from ativo.models import Ativo
from integracao.tasks import buscar_cotacoes_task

@receiver(post_save, sender=Ativo)
def iniciar_busca_apos_criacao_ativo(sender, instance, created, **kwargs):
    """
    Dispara a tarefa Celery para buscar cotações ao adicionar um novo ativo.
    """
    if created:
        moeda = instance.moeda
        data_compra = instance.data_compra
        buscar_cotacoes_task.delay(moeda.id, data_compra)
