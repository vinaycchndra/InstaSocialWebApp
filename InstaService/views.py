from rest_framework.views import APIView
from instagram.CustomPermission import IsSessionActive
from .serializers import CreatePostSerializer, UpdatePostSerializer, FollowerSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Posts, Followers, Likes
from user.models import CustomUser
from UserFeedService.tasks import add_feed, remove_feed, after_post_feed, remove_deleted_post
from .tasks import create_and_push_notification


def get_errors(serializer):
    error_msg = {}
    for field in serializer.errors:
        error_msg[field] = str(serializer.errors[field][0])
    return Response({'error_msg': error_msg, 'data': {}, 'msg': 'Not valid'}, status=status.HTTP_400_BAD_REQUEST)


class InstaPost(APIView):
    permission_classes = [IsSessionActive]

    def post(self, request):
        data = request.data.copy()
        data['posted_by'] = request.user.id
        serializer = CreatePostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            # Getting the list of all the followers of the user
            post_id = serializer.data['id']
            user_id = serializer.data['posted_by']
            all_follower_ids = list(Followers.objects.filter(followed__id=user_id).values_list('followe_by', flat=True))

            # Task invocation to add post into all the followers' feed and pushing notification
            after_post_feed.apply_async((post_id, all_follower_ids, user_id), countdown=0, retry=True,
                                        retry_policy={'max_retries': 3})

            # Task invocation to push notification into User's Notification section in real time...
            user_obj = CustomUser.objects.get(id=user_id)
            mssg = " %s just  posted..." % (user_obj.get_full_name())
            create_and_push_notification.apply_async((mssg, all_follower_ids), countdown=0, retry=True,
                                                     retry_policy={'max_retries': 3})
            return Response({'msg': 'Post created successfully !!!', 'data': serializer.data, 'error_msg': {}},
                            status=status.HTTP_201_CREATED)
        return get_errors(serializer)

    def patch(self, request, pk):
        post_obj = self.get_object(pk)
        if post_obj:
            if request.user.id == post_obj.posted_by.id:
                serializer = UpdatePostSerializer(post_obj, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'data': serializer.data, 'msg': 'Ok', 'error_msg': {}}, status=status.HTTP_200_OK)
                return get_errors(serializer)
            return Response({'data': {}, 'msg': 'You do not have permission to edit this post', 'error_msg': {}},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'data': {}, 'msg': 'Not Found !', 'error_msg': {}}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        post_obj = self.get_object(pk)
        if post_obj:
            serializer = CreatePostSerializer(post_obj)
            return Response({'data': serializer.data, 'msg': 'Ok', 'error_msg': {}}, status=status.HTTP_200_OK)
        return Response({'data': {}, 'msg': 'Post does not exist', 'error_msg': {}}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        post_obj = self.get_object(pk)
        if post_obj:
            if request.user.id == post_obj.posted_by.id:
                post_obj.delete()

                # task to remove all the stream objects which have post_id which is deleted by now
                remove_deleted_post.apply_async((pk,), countdown=0, retry=True,
                                                retry_policy={'max_retries': 3})

                return Response({'data': {}, 'msg': 'Deleted Successfully !', 'error_msg': {}},
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'data': {}, 'msg': 'You do not have permission to edit this post', 'error_msg': {}},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'data': {}, 'msg': 'Post does not exist', 'error_msg': {}},
                        status=status.HTTP_404_NOT_FOUND)

    def get_object(self, pk):
        try:
            obj = Posts.objects.get(id=pk)
        except Posts.DoesNotExist:
            obj = None
        return obj


# Follo and Unfollow a User class view is implemented here...
class FollowUserView(APIView):
    permission_classes = [IsSessionActive]

    def post(self, request, pk):
        followed = self.get_user(pk)
        if followed:
            try:
                follow_followee_obj = Followers.objects.get(followed__id=followed.id, followe_by__id=request.user.id)
            except Followers.DoesNotExist:
                follow_followee_obj = None

            if follow_followee_obj:
                follow_followee_obj.delete()

                # Removing all the posts of the unfollowed user from the user's feed
                remove_feed.apply_async((followed.id, request.user.id), countdown=0, retry=True,
                                        retry_policy={'max_retries': 3})

                return Response({'msg': 'You have unfollowed {}!!!'.format(followed.get_full_name()),
                                 'data': {}, 'error_msg': {}},
                                status=status.HTTP_200_OK)

            data = request.data.copy()
            data['followed'] = followed.id
            data['followe_by'] = request.user.id
            serializer = FollowerSerializer(data=data)
            if serializer.is_valid():
                serializer.save()

                # getting 10 recent posts of the person being followed
                followed_id = serializer.data['followed']
                followe_by_id = serializer.data['followe_by']
                post_list = list(Posts.objects.filter(posted_by__id=followed_id)[:10].values_list('id', flat=True))

                # passing tasks to the celery
                add_feed.apply_async((post_list, followed_id, followe_by_id), countdown=0, retry=True,
                                     retry_policy={'max_retries': 3})

                return Response({'msg': 'You  successfully started following {}!!!'.format(followed.get_full_name()),
                                 'data': serializer.data, 'error_msg': {}}, status=status.HTTP_201_CREATED)
            return get_errors(serializer)
        return Response({'data': {}, 'msg': 'User does not exist', 'error_msg': {}},
                        status=status.HTTP_404_NOT_FOUND)

    def get_user(self, pk):
        try:
            obj = CustomUser.objects.get(id=pk)
        except CustomUser.DoesNotExist:
            obj = None
        return obj


# Class view to like or dislike a post
class LikeDislikePost(APIView):
    permission_classes = [IsSessionActive]

    def post(self, request, pk):
        # Looking if a post object exists which is to be liked
        try:
            post = Posts.objects.get(id=pk)
        except Posts.DoesNotExist:
            return Response({'data': {}, 'msg': 'No such Post exists', 'error_msg': {}},
                            status=status.HTTP_404_NOT_FOUND)
        user = request.user

        #  Looking if a user already Liked the post if it is than we delete the like else we create a new like instance
        try:
            like = Likes.objects.get(parent_post_id__id=pk, user__id=user.id)
            like.delete()
            return Response({'data': {'liked': False}, 'msg': 'Disliked', 'error_msg': {}},
                            status=status.HTTP_201_CREATED)
        except Likes.DoesNotExist:
            like = Likes.objects.create(parent_post_id=post, user=user)

        return Response({'data': {'liked': True}, 'msg': 'Liked', 'error_msg': {}},
                        status=status.HTTP_201_CREATED)


# Class view to like or dislike a comment
class LikeDislikeComment(APIView):
    permission_classes = [IsSessionActive]

    def post(self, request, pk):
        # Looking if a post object exists which is to be liked
        try:
            post = Posts.objects.get(id=pk)
        except Posts.DoesNotExist:
            return Response({'data': {}, 'msg': 'No such Post exists', 'error_msg': {}},
                            status=status.HTTP_404_NOT_FOUND)
        user = request.user

        #  Looking if a user already Liked the post if it is than we delete the like else we create a new like instance
        try:
            like = Likes.objects.get(parent_post_id__id=pk, user__id=user.id)
            like.delete()
            return Response({'data': {'liked': False}, 'msg': 'Disliked', 'error_msg': {}},
                            status=status.HTTP_201_CREATED)
        except Likes.DoesNotExist:
            like = Likes.objects.create(parent_post_id=post, user=user)

        return Response({'data': {'liked': True}, 'msg': 'Liked', 'error_msg': {}},
                        status=status.HTTP_201_CREATED)









