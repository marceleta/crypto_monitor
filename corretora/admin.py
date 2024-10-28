from django.contrib import admin
from .models import TipoOperacao, CorretoraConfig

# Registrar os modelos no admin
admin.site.register(TipoOperacao)
admin.site.register(CorretoraConfig)

