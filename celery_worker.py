"""
Celery Video Transcoder worker

Author: Snehangshu Bhattacharya
Maintainer: Snehangshu Bhattacharya
"""

__author__ = "Snehangshu Bhattacharya"
__maintainer__ = "Snehangshu Bhattacharya"
__email__ = "hello@snehangshu.dev"

from celery import Celery

app = Celery('celery-video-transcoder',
             backend='redis://localhost:6379/0',
             broker='amqp://guest@localhost//',
             include=['helpers.video'])
