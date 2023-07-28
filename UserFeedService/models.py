from django.db import models


# Adding  a stream table with user_id, post_id, follower_id
class StreamTable(models.Model):
    user_id = models.IntegerField(null=False)
    post_id = models.IntegerField(null=False)
    followed_user_id = models.IntegerField(null=False)

    def __str__(self):
        return self.id
