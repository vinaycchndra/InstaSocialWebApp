from rest_framework import serializers
from .models import Posts, Followers, Comments


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


# Create Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ['id', 'user', 'post', 'photo', 'comment']

    def validate(self, attrs):
        photo = attrs.get('photo')
        comment = attrs.get('comment')

        if photo is None and (comment is None or len(comment) == 0):
            raise serializers.ValidationError('Both comment and photo cannot be null')
        return attrs

