from django.db import models
from moeda.models import Moeda
from usuario.models import Usuario

class Ativo(models.Model):
    moeda = models.ForeignKey(Moeda, on_delete=models.CASCADE)  # Relaciona o ativo à moeda cadastrada
    data_compra = models.DateField()
    valor_compra = models.DecimalField(max_digits=12, decimal_places=2)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Relaciona o ativo ao usuário que comprou

    def __str__(self):
        return f'{self.moeda.nome} - {self.data_compra}'

