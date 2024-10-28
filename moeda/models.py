from django.db import models
from usuario.models import Usuario
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Moeda(models.Model):
    nome = models.CharField(max_length=100)
    token = models.CharField(max_length=10, unique=True)
    cor = models.CharField(max_length=7, default='#FF5733')
    logo = models.ImageField(upload_to='logos_moedas/', blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Relaciona com o usuário personalizado
    
    # Campos para a relação genérica
    corretora_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    corretora_object_id = models.PositiveIntegerField(null=True, blank=True)
    corretora = GenericForeignKey('corretora_content_type', 'corretora_object_id')

    def __str__(self):
        return self.nome
    

class HistoricoCotacao(models.Model):
    moeda = models.ForeignKey(Moeda, on_delete=models.CASCADE)  # Relaciona com a moeda
    data = models.DateField(null=True)  # Data da cotação
    abertura = models.DecimalField(max_digits=20, decimal_places=10, default=0)  # Preço de abertura no dia
    fechamento = models.DecimalField(max_digits=20, decimal_places=10, default=0)  # Preço de fechamento no dia
    alta = models.DecimalField(max_digits=20, decimal_places=10, default=0)  # Preço mais alto no dia
    baixa = models.DecimalField(max_digits=20, decimal_places=10, default=0)  # Preço mais baixo no dia
    volume = models.DecimalField(max_digits=20, decimal_places=10, default=0)  # Volume negociado no dia

    class Meta:
        unique_together = ('moeda', 'data')  # Garante que só haverá uma cotação por moeda por dia

    def __str__(self):
        return f'{self.moeda.nome} - {self.data} - Abertura: {self.abertura} - Fechamento: {self.fechamento}'


