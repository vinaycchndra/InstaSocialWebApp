from rest_framework import serializers
from .models import Posts


class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['posted_by', 'message', 'image']
