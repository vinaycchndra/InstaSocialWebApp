from rest_framework.views import APIView
from instagram.CustomPermission import IsSessionActive
from .serializers import CreatePostSerializer, UpdatePostSerializer, FollowerSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Posts, Followers
from user.models import CustomUser


# function to get errors from the serializer object
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
            else:
                return Response({'data': {}, 'msg': 'You do not have permission to edit this post', 'error_msg': {}},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'data': {}, 'msg': 'Not Found !', 'error_msg': {}}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        post_obj = self.get_object(pk)
        if post_obj:
            serializer = CreatePostSerializer(post_obj)
            return Response({'data': serializer.data, 'msg': 'Ok', 'error_msg': {}}, status=status.HTTP_200_OK)
        else:
            return Response({'data': {}, 'msg': 'Post does not exist', 'error_msg': {}}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        post_obj = self.get_object(pk)
        if post_obj:
            if request.user.id == post_obj.posted_by.id:
                post_obj.delete()
                return Response({'data': {}, 'msg': 'Deleted Successfully !', 'error_msg': {}},
                                status=status.HTTP_204_NO_CONTENT)

            return Response({'data': {}, 'msg': 'You do not have permission to edit this post', 'error_msg': {}},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'data': {}, 'msg': 'Post does not exist', 'error_msg': {}},
                            status=status.HTTP_404_NOT_FOUND)

    def get_object(self, pk):
        try:
            obj = Posts.objects.get(id=pk)
        except Posts.DoesNotExist:
            obj = None
        return obj


# Follower class view implemented
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
                return Response({'msg': 'You have unfollowed {}!!!'.format(followed.get_full_name()),
                                 'data': {}, 'error_msg': {}},
                                status=status.HTTP_204_NO_CONTENT)
            else:
                data = request.data.copy()
                data['followed'] = followed.id
                data['followe_by'] = request.user.id
                serializer = FollowerSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'msg': 'You  successfully started following {}!!!'.format(followed.get_full_name()),
                                     'data': serializer.data, 'error_msg': {}}, status=status.HTTP_201_CREATED)
                return get_errors(serializer)

        else:
            return Response({'data': {}, 'msg': 'User does not exist', 'error_msg': {}},
                            status=status.HTTP_404_NOT_FOUND)

    def get_user(self, pk):
        try:
            obj = CustomUser.objects.get(id=pk)
        except CustomUser.DoesNotExist:
            obj = None
        return obj