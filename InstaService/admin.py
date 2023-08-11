from django.contrib import admin
from .models import Posts, Likes, Comments, Followers, Notification

admin.site.register(Posts)
admin.site.register(Likes)
admin.site.register(Comments)
admin.site.register(Followers)
admin.site.register(Notification)
