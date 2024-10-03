from django.db import models
from usuario.models import Usuario

class CorretoraConfig(models.Model):
    TIPO_CHOICES = [
        ('spot', 'Spot'),
        ('futures', 'Futures'),
        ('margin', 'Margin'),
        # Adicione mais tipos conforme necessário
    ]

    nome = models.CharField(max_length=50, unique=True)
    url_base = models.URLField()
    exige_passphrase = models.BooleanField(default=False)
    tipos_suportados = models.ManyToManyField('TipoOperacao', blank=True)  # Armazena os tipos suportados pela corretora
    logo = models.ImageField(upload_to='logos_corretoras/', null=True, blank=True)  # Campo para upload do logo

    def __str__(self):
        return self.nome


class TipoOperacao(models.Model):
    tipo = models.CharField(max_length=50, choices=[('spot', 'Spot'), ('futures', 'Futures'), ('margin', 'Margin')])

    def __str__(self):
        return self.tipo


class CorretoraUsuario(models.Model):
    corretora = models.ForeignKey(CorretoraConfig, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)
    passphrase = models.CharField(max_length=255, null=True, blank=True)
    tipos = models.ManyToManyField(TipoOperacao)  # Permite associar múltiplos tipos de operações
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.corretora.nome} - {self.usuario.username}"
    


