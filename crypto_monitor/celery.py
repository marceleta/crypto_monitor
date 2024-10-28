from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Define o módulo de configuração padrão do Django para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_monitor.settings')

app = Celery('crypto_monitor')

# Lê as configurações do Django no namespace CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre automaticamente as tarefas (tasks) nos apps instalados
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
