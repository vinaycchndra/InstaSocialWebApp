from django.contrib import admin
from .models import Posts, Likes, Comments, Followers

admin.site.register(Posts)
admin.site.register(Likes)
admin.site.register(Comments)
admin.site.register(Followers)
