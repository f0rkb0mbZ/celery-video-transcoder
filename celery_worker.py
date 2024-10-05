from celery import Celery

app = Celery('celery-video-transcoder',
             backend='redis://localhost:6379/0',
             broker='amqp://guest@localhost//',
             include=['helpers.video'])
