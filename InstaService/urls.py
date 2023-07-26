from django.urls import path
from .views import InstaPost

urlpatterns = [
    path('post_ops/', InstaPost.as_view(), name='create_post'),
    path('post_ops/<int:pk>/', InstaPost.as_view(), name='update_get_delete_post'),
]