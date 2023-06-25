import os
from celery import Celery
from . import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TempoMail.settings')

app = Celery('TempoMail',
             broker=f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}/{config.REDIS_DB}')

app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
        print(f'Request: {self.request!r}')