from celery import shared_task
from time import sleep


@shared_task(bind=True)
def add(self, x, y):
    return x+y, 'Hello'
