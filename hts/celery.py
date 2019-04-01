
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django_celery_beat import *
import django
import datetime
from celery.schedules import crontab
from datetime import timedelta
# set the default Django settings module for the 'celery' program.
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hts.settings')
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hts.settings')

app = Celery('hts')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hts.settings')
django.setup()
#app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
#app.autodiscover_tasks()

imports = ('hts_backend.tasks',)

app.config_from_object('django.conf:settings')
app.conf.update(
    enable_utc=True,
    broker_url='amqp://guest:guest@localhost:5672//',
    timezone='Asia/Seoul',
)

"""

    'Order-Treatment-Alg': {
        'task': 'hts_backend.tasks.Order_Treatment_Alg',
        'schedule': timedelta(seconds=10),
        'args': ()

    },

"""

app.conf.beat_schedule = {

    'RD-Modifying': {
        'task': 'hts_backend.tasks.RD_Modifying',
        'schedule': timedelta(seconds=3),
        'args': ()
    },
    'Order-Treatment-Alg': {
        'task': 'hts_backend.tasks.Order_Treatment_Alg',
        'schedule': timedelta(seconds=2),
        'args': ()
    },
    'JeongSan-Company': {
        'task': 'hts_backend.tasks.JeongSan_Company',
        'schedule': timedelta(seconds=60),
        'args': ()
    },

}
"""
   
'JeongSan': {
    'task': 'hts_backend.tasks.JeongSan',
    'schedule': crontab(minute=30, hour=15, day_of_week='mon-fri'),
    'args': ()
    }
},"""


"""
'Order-Treatment-Alg': {
    'task': 'hts_backend.tasks.Order_Treatment_Alg',
    'schedule': 10,
    'args': ()
},"""

"""
imports = ('hts_backend.tasks',)
app = Celery('hts', broker='amqp://guest:guest@localhost:5672//')
# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
#app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
#app.autodiscover_tasks()
#app.autodiscover_tasks('hts.settings.INSTALLED_APPS')
#'redis://localhost:6379'
app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'hts_backend.tasks.mysum',
        'schedule': 5.0,
        'args': (16, 16)
    },
}"""
"""

imports = ('hts_backend.tasks',)
app.conf.update(
    BROKER_URL='django://',
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='Asia/Seoul',
    CELERY_ENABLE_UTC=False,
)
"""
"""
app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'tasks.mysum',
        'schedule': 5.0,
        'args': (16, 16)
    },
}
"""

#시간과 주기에 의한 통제가 안 되고 있다.


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

#celery worker -A hts   :default execute - in manage.py's url
#App 예하 task들은 setting을 통해 설정 가능



