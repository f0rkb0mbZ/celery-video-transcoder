"""
Celery Video Transcoder worker

Author: Snehangshu Bhattacharya
Maintainer: Snehangshu Bhattacharya
"""

__author__ = "Snehangshu Bhattacharya"
__maintainer__ = "Snehangshu Bhattacharya"
__email__ = "hello@snehangshu.dev"

import os
from celery import Celery

app = Celery('celery-video-transcoder',
             backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
             broker=os.getenv('CELERY_BROKER_URL', 'amqp://guest@localhost//'),
             include=['helpers.video'])
