from rest_framework import serializers
from .models import Posts


# Create Post Serializer
class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['id', 'posted_by', 'message', 'image']


# Update Post Serializer
class UpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['message', 'image']


