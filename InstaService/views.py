from rest_framework.views import APIView
from instagram.CustomPermission import IsSessionActive
from .serializers import CreatePostSerializer, UpdatePostSerializer, FollowerSerializer, CommentSerializer, ListCommentSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Posts, Followers, Likes, Comments
from user.models import CustomUser
from UserFeedService.tasks import add_feed, remove_feed, after_post_feed, remove_deleted_post
from .tasks import create_and_push_notification
from django.db.models import Case, BooleanField, Value, When


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
                                status=status.HTTP_200_OK)
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
            return Response({'data': {'liked': False}, 'msg': 'Unliked', 'error_msg': {}},
                            status=status.HTTP_201_CREATED)
        except Likes.DoesNotExist:
            like = Likes.objects.create(parent_post_id=post, user=user)

        return Response({'data': {'liked': True}, 'msg': 'Liked', 'error_msg': {}},
                        status=status.HTTP_201_CREATED)


# Class view to like or dislike a comment
class LikeDislikeComment(APIView):
    permission_classes = [IsSessionActive]

    def post(self, request, pk):
        # Looking if a comment object exists with comment_id which is to be liked or disliked.
        try:
            post = Comments.objects.get(id=pk)
        except Comments.DoesNotExist:
            return Response({'data': {}, 'msg': 'No such comment exists', 'error_msg': {}},
                            status=status.HTTP_404_NOT_FOUND)
        user = request.user

# Looking if a user already Liked the comment if it is than we delete the like else we create a new like instance
        try:
            like = Likes.objects.get(parent_comment_id__id=pk, user__id=user.id)
            like.delete()
            return Response({'data': {'liked': False}, 'msg': 'Unliked', 'error_msg': {}},
                            status=status.HTTP_201_CREATED)
        except Likes.DoesNotExist:
            like = Likes.objects.create(parent_comment_id=post, user=user)

        return Response({'data': {'liked': True}, 'msg': 'Liked the comment', 'error_msg': {}},
                        status=status.HTTP_201_CREATED)


class CommentView(APIView):
    permission_classes = [IsSessionActive]

    def get(self, request, pk):
        comment_obj = self.get_comment(pk)
        if comment_obj:
            serializer = CommentSerializer(comment_obj)
            return Response({'data': serializer.data, 'msg': 'Ok', 'error_msg': {}}, status=status.HTTP_200_OK)
        return Response({'data': {}, 'msg': 'Not Found !', 'error_msg': {}}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        # if a post object exists on which comment needs to be post and here the pk is the post id not the comment id
        post = self.get_post(pk)
        if post is None:
            return Response({'data': {}, 'msg': 'No such Post exists', 'error_msg': {}},
                            status=status.HTTP_404_NOT_FOUND)
        user = request.user
        data = request.data.copy()
        data['post'] = post.id
        data['user'] = user.id
        serializer = CommentSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Commented successfully !!!', 'data': serializer.data, 'error_msg': {}},
                            status=status.HTTP_201_CREATED)
        else:
            return get_errors(serializer)

    def patch(self, request, pk):
        comment_obj = self.get_comment(pk)
        if comment_obj:
            if request.user.id == comment_obj.user.id:
                serializer = CommentSerializer(comment_obj, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'data': serializer.data, 'msg': 'Ok', 'error_msg': {}}, status=status.HTTP_200_OK)
                return get_errors(serializer)
            return Response({'data': {}, 'msg': 'You do not have permission to edit this comment', 'error_msg': {}},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'data': {}, 'msg': 'Not Found !', 'error_msg': {}}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        comment_obj = self.get_comment(pk)
        if comment_obj:
            if request.user.id == comment_obj.user.id:
                comment_obj.delete()
                return Response({'data': {}, 'msg': 'Deleted Successfully !', 'error_msg': {}},
                                status=status.HTTP_200_OK)
            return Response({'data': {}, 'msg': 'You do not have permission to delete this comment', 'error_msg': {}},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'data': {}, 'msg': 'Not Found !', 'error_msg': {}}, status=status.HTTP_404_NOT_FOUND)

    def get_post(self, pk):
        try:
            post = Posts.objects.get(id=pk)
        except Posts.DoesNotExist:
            return None

        return post

    def get_comment(self, pk):
        try:
            comment = Comments.objects.get(id=pk)
        except Comments.DoesNotExist:
            return None

        return comment


# Get Api to send back the all the comments on a particular post when user
# requests it with label of user's comment and liked comment
class AllCommentsPost(APIView):
    permission_classes = [IsSessionActive]

    def get(self, request, pk):
        try:
            post = Posts.objects.get(id=pk)
        except Posts.DoesNotExist:
            return Response({'data': {}, 'msg': 'No such Post exists', 'error_msg': {}},
                            status=status.HTTP_404_NOT_FOUND)

        # querying all the Like of the user from the Like model for comments
        # to get all the comments which are liked by user which can be used below to
        # set status of the comments which is liked or not by the user who is requesting all the comments on a post

        liked_comment_ids = Likes.objects.filter(user__id=request.user.id, parent_post_id=None).\
            values_list('parent_comment_id', flat=True)
        liked_comment_ids_set = set(liked_comment_ids)

        # Writing a case statement in the django query to add the another field which
        # defines if you liked that particular comment or not
        case1 = [
            When(user__id=request.user.id, then=Value(True)),
        ]

        case2 = [
            When(id__in=liked_comment_ids_set, then=Value(True)),
        ]

        your_comment = Case(*case1, default=Value(False), output_field=BooleanField())
        you_liked = Case(*case2, default=Value(False), output_field=BooleanField())

        comments = Comments.objects.annotate(your_comment=your_comment, you_liked=you_liked).filter(post__id=pk).\
            order_by('-created_at')
        serializer = ListCommentSerializer(comments, many=True)
        return Response({'data': serializer.data, 'msg': 'Ok', 'error_msg': {}}, status=status.HTTP_200_OK)






