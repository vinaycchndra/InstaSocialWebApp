from django.db import models
from user.models import CustomUser


# Post Table
class Posts(models.Model):
    posted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    message = models.CharField(max_length=1000, blank=True)
    image = models.ImageField(blank=False, upload_to='images/')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-create_time']

    def __str__(self):
        if self.posted_by:
            return 'Post by: '+self.posted_by.get_full_name()
        return 'User has been deleted'

# Follower Table: followee != follower
class Followers(models.Model):
    followed = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followed')
    followe_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followed_by')
    following_since = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s is being followed by %s" % (self.followed.get_full_name(), self.followe_by.get_full_name())


class Comments(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='images/', blank=True, null=True)
    comment = models.CharField(max_length=2000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s commented on %s's  post" % (self.user.get_full_name(), self.post.posted_by.get_full_name())


# Like table for both
class Likes(models.Model):
    parent_post_id = models.ForeignKey(Posts, on_delete=models.CASCADE, blank=True, null=True)
    parent_comment_id = models.ForeignKey(Comments, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.parent_comment_id is None:
            s = "%s liked  %s's  post" % (self.user.get_full_name(), self.parent_post_id.posted_by.get_full_name())
        else:
            s = "%s liked %s's comment" % (self.user.get_full_name(), self.parent_comment_id.user.get_full_name())
        return s


class Notification(models.Model):
    notification = models.CharField(max_length=1000)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)


# One to One field for post to store the like count
class LikeCountPost(models.Model):
    like_count = models.IntegerField(default=0)
    post = models.OneToOneField(Posts, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)


# One to One field for comment to store the like count on a comment
class LikeCountComment(models.Model):
    like_count = models.IntegerField(default=0)
    comment = models.OneToOneField(Comments, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)
