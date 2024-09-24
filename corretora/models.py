from django.db import models
from usuario.models import Usuario

class AbstractCorretora(models.Model):
    nome = models.CharField(max_length=100)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)
   
    class Meta:
        abstract = True  # Define que esta é uma classe abstrata

    def __str__(self):
        return self.nome
    
class BybitCorretora(AbstractCorretora):
    pass


