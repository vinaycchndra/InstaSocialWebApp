from django.db import models
from user.models import CustomUser


# Post Table
class Posts(models.Model):
    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=1000, blank=True)
    image = models.ImageField(blank=False, upload_to='images/')
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Post by: '+self.posted_by.get_full_name()


# Follower Table: followee != follower
class Followers(models.Model):
    followed = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followed')
    followe_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followed_by')
    following_since = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s is being followed by %s" % (self.followee.get_full_name(), self.follower.get_full_name())


class Comments(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    is_picture = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='images/', blank=True)
    comment = models.CharField(max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s commented on %s's  post" % (self.user.get_full_name(), self.post.posted_by.get_full_name())


# Like table for both
class Likes(models.Model):
    parent_post_id = models.ForeignKey(Posts, on_delete=models.CASCADE, blank=True)
    parent_comment_id = models.ForeignKey(Comments, on_delete=models.CASCADE, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        if self.parent_comment_id==None:
            s = "%s liked  %s's  post" % (self.user.get_full_name(), self.parent_post_id.posted_by.get_full_name())
        else:
            s = "%s liked %s's comment" % (self.user.get_full_name(), self.parent_comment_id.user.get_full_name())

        return s
