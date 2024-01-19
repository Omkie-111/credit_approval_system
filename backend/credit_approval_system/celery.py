from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_approval_system.settings')

# Create a Celery instance and configure it using the settings from Django.
app = Celery('credit_approval_system')
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_backend='redis://redis:6379/0',
)

app.conf.enable_utc = False
app.conf.update(timezone='UTC')

# Load task modules from all registered Django app configs.
app.config_from_object(settings, namespace='CELERY')

# Auto-discover tasks in all installed apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
