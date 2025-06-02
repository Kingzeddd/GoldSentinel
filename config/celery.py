import os
from celery import Celery

# Définir le module de settings par défaut pour Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Créer l'instance Celery
app = Celery('config')

# Charger les configurations depuis les settings Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches dans les applications Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')