from celery import shared_task
from .models import Notification
from user.models import CustomUser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# Notification tasks creating and pushing into the user's notification section in real time...
@shared_task(bind=True, queue='Notification_Service_Que')
def create_and_push_notification(self, mssg, follower_list):
    for id_ in follower_list:
        try:
            user = CustomUser.objects.get(id=id_)
            Notification.objects.create(user=user, notification=mssg)
        except CustomUser.DoesNotExist:
            pass

        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(str(id_), {'type': 'chat.notification', 'text': mssg})
        except Exception as e:
            print(e)
    return 'Created and Pushed in for online user'




