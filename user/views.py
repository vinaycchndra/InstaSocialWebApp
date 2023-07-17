from django.shortcuts import render
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer
from rest_framework import status
from rest_framework.views import APIView


class UserRegistrationView(APIView):

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({'message': 'Registration Successfull'}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
