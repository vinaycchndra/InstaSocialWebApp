from django.urls import path
from .views import Get_Feed

urlpatterns = [
    path('feed/', Get_Feed.as_view(), name='get_user_feed'),
]
