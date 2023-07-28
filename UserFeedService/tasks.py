from celery import shared_task
from time import sleep


@shared_task(bind=True, queue='Feed_Service_Que')
def add_feed(self, x, y):
    for i in range(5):
        sleep(1)
    return x+y



