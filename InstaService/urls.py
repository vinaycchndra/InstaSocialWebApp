from django.urls import path
from .views import InstaPost, FollowUserView, LikeDislikePost, LikeDislikeComment, CommentView, AllCommentsPost

urlpatterns = [
    path('post_ops/', InstaPost.as_view(), name='create_post'),
    path('post_ops/<int:pk>/', InstaPost.as_view(), name='update_get_delete_post'),
    path('follow/<int:pk>/', FollowUserView.as_view(), name='follow_user'),
    path('comment_post/<int:pk>/', CommentView.as_view(), name='comment_on_post'),
    path('like_post/<int:pk>/', LikeDislikePost.as_view(), name='like_a_post'),
    path('like_comment/<int:pk>/', LikeDislikeComment.as_view(), name='like_a_comment'),
    path('post_comments/<int:pk>/', AllCommentsPost.as_view(), name='comments_on_a_post'),
]
