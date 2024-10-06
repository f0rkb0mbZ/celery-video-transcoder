# celery-video-transcoder

FastAPI and Celery pipeline for bulk video transcode - to simulate YouTube uploads.

This repository is a part of my blog
on [Distributed Computing with Python: Unleashing the Power of Celery for Scalable Applications](https://blogs.snehangshu.dev/mastering-distributed-computing-with-python-unleashing-the-power-of-celery-for-scalable-applications).
Follow it for detailed instructions.

### Install Redis and RabbitMQ in your system or run the given `docker-compose.yml`
```bash
docker compose up
```
Once the containers are stated, Redis will be available at `redis://localhost:6379` and RabbitMQ will be available at `rabbitmq://localhost:5672`
### Install ffmpeg in your system
```bash
sudo apt install ffmpeg # Assuming ubuntu / debian system
```
For other os, please follow the official [guide](https://www.ffmpeg.org/download.html).
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
