from rest_framework import serializers
from .models import Posts, Followers


# Create Post Serializer
class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['id', 'posted_by', 'message', 'image', 'create_time']


# Update Post Serializer
class UpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['message', 'image']


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Followers
        fields = '__all__'

    def validate(self, attrs):
        follower_id = attrs.get('followe_by')
        followee_id = attrs.get('followed')

        if follower_id == followee_id:
            raise serializers.ValidationError('You can not follow yourself')
        return attrs




