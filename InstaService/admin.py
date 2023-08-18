from django.contrib import admin
from .models import Posts, Likes, Comments, Followers, Notification, LikeCountPost, LikeCountComment

admin.site.register(Posts)
admin.site.register(Likes)
admin.site.register(Comments)
admin.site.register(Followers)
admin.site.register(Notification)
admin.site.register(LikeCountPost)
admin.site.register(LikeCountComment)
