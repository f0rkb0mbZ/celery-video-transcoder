from celery import Celery

app = Celery('hello', broker='amqp://guest@localhost//', include=['helpers.video'])
app.autodiscover_tasks()


@app.task
def hello():
    print('Hello World!')

# hello.delay()