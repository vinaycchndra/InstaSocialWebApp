from rest_framework.views import APIView
from instagram.CustomPermission import IsSessionActive
from .serializers import CreatePostSerializer
from rest_framework.response import Response
from rest_framework import status


class InstaPost(APIView):
    permission_classes = [IsSessionActive]

    def post(self, request):
        data = request.data.copy()
        data['posted_by'] = request.user.id

        serializer = CreatePostSerializer(data=data)
        if serializer.is_valid():
            post_obj = serializer.save()
            return Response({'msg': 'Post created successfully !!!'}, status=status.HTTP_201_CREATED)

        error_msg = {}
        for field in serializer.errors:
            error_msg[field] = str(serializer.errors[field][0])
        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)