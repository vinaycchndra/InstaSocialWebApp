from django.urls import path
from .views import InstaPost

urlpatterns = [
    path('create_post/', InstaPost.as_view(), name='create_post'),
]