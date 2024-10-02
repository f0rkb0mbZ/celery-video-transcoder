from celery import Celery

app = Celery('hello', backend='redis://localhost:6379/0', broker='amqp://guest@localhost//', include=['helpers.video'])
app.conf.update(task_ignore_result=False) # result_backend='redis://localhost:6379/0',
app.autodiscover_tasks()


@app.task
def hello():
    print('Hello World!')

# hello.delay()