from django.urls import path
from .views import InstaPost, FollowUserView

urlpatterns = [
    path('post_ops/', InstaPost.as_view(), name='create_post'),
    path('post_ops/<int:pk>/', InstaPost.as_view(), name='update_get_delete_post'),
    path('follow/<int:pk>/', FollowUserView.as_view(), name='follow_user'),

]