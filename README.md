# celery-video-transcoder

FastAPI and Celery pipeline for bulk video transcode - to simulate YouTube uploads

This repository is a part of my blog
on [Distributed computing with Python: A comprehensive guide to Celery](/distributed-computing-with-python-a-comprehensive-guide-to-celery).
Follow it for detailed instructions.

### Create python a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the FastAPI server

```bash
fastapi run api.py
```

### Run the Celery worker

```bash
celery -A celery_worker worker
```
