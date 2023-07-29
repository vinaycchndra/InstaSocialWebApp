from .models import StreamTable
from rest_framework.views import APIView
from rest_framework.response import Response
from InstaService.models import Posts
from InstaService.serializers import CreatePostSerializer
from instagram.CustomPermission import IsSessionActive


class Get_Feed(APIView):
    permission_classes = [IsSessionActive]

    def get(self, request):
        user_id = request.user.id
        # querying all the feeds of the user from the stream table database
        post_ids = StreamTable.objects.filter(user_id=user_id).values_list('post_id', flat=True)
        post_ids_set = set(post_ids)
        post_list = Posts.objects.filter(id__in=post_ids_set)
        serializer = CreatePostSerializer(post_list, many=True)
        return Response({'data': serializer.data, 'msg': 'Ok', 'error_msg': {}})








