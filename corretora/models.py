from django.db import models
from usuario.models import Usuario

class Corretora(models.Model):

    SUPPORTED_CORRETORAS = [
        ('bybit', 'Bybit'),
        # Adicionar outras corretoras aqui no futuro, se necessário.
    ]

    nome = models.CharField(max_length=50, choices=SUPPORTED_CORRETORAS)
    url_base = models.URLField()
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)
    passphrase = models.CharField(max_length=255, null=True, blank=True)  # Necessário para algumas corretoras
    tipo = models.CharField(max_length=50)  # Ex: 'spot', 'futures', etc.
    logo = models.ImageField(upload_to='corretora_logos/', null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    


