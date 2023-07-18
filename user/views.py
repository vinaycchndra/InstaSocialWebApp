from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, LoginSerializer
from rest_framework import status, permissions
from rest_framework.views import APIView
from .models import LoginSession


class UserRegistrationView(APIView):

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({'message': 'Registration Successfull'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login Function
class LoginView(APIView):
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            try:
                session = LoginSession.objects.get(user__id=user.id)
                if session.is_session_expired():
                    session.delete()
                else:
                    return Response({'msg': 'You session is active already from other device kindy logout to use'})
            except LoginSession.DoesNotExist:
                pass
            LoginSession.objects.create(user=user)
            tokens = user.get_tokens_for_user()
            return Response({'msg': 'Login Success', 'token': tokens})
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        try:
            session = LoginSession.objects.get(user__id=request.user.id)
            session.delete()
            return Response({"msg": "You are Successfully Logged-out of the API"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

