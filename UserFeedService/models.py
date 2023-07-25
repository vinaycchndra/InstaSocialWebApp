from django.db import models


class StreamTable(models.Model):
    user_id = models.IntegerField(null=False)
    post_id = models.IntegerField(null=False)

    def __str__(self):
        return self.id
