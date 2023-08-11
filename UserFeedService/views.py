from .models import StreamTable
from rest_framework.views import APIView
from rest_framework.response import Response
from InstaService.models import Posts, Likes
from InstaService.serializers import CreatePostSerializer
from instagram.CustomPermission import IsSessionActive


class Get_Feed(APIView):
    permission_classes = [IsSessionActive]

    def get(self, request):
        user_id = request.user.id

        # querying all the feeds of the user from the stream table database
        post_ids = StreamTable.objects.filter(user_id=user_id).values_list('post_id', flat=True)
        post_ids_set = set(post_ids)

        # Now using the post ids , getring post objects to be sent to the user requesting the feed
        post_list = Posts.objects.filter(id__in=post_ids_set)
        serializer = CreatePostSerializer(post_list, many=True)

        # Getting all the likes for the posts for the user to check wether user has already liked the post or not
        liked_posts = Likes.objects.filter(user__id=user_id, parent_comment_id=None).\
            values_list('parent_post_id', flat=True)
        liked_post_set = set(liked_posts)

        # Now updating the data obtained from the serializer to add if the post is liked by the user or not
        data = serializer.data
        for ord_dict in data:
            if ord_dict['id'] in liked_post_set:
                ord_dict['liked'] = True
            else:
                ord_dict['liked'] = False
        return Response({'data': data, 'msg': 'Ok', 'error_msg': {}})








