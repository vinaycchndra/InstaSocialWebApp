from rest_framework.response import Response
from .serializers import UserRegistrationSerializer, LoginSerializer, UpdatePasswordSerializer
from rest_framework import status, permissions
from rest_framework.views import APIView
from .models import LoginSession
from instagram.CustomPermission import IsSessionActive

class UserRegistrationView(APIView):

    def post(self, request,):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Registration Successfull'}, status=status.HTTP_201_CREATED)
        else:

            error_msg = serializer.__dict__['_kwargs']['data'].copy()
            error_msg['extra_error'] = ""
            for field in error_msg:
                if field in serializer.errors:
                    error_msg[field] = str(serializer.errors[field][0])
                else:
                    error_msg[field] = ""
            print(serializer.errors)
            if 'non_field_errors' in serializer.errors:
                error_msg['extra_error'] = str(serializer.errors['non_field_errors'][0])

            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)


# Login Function
class LoginView(APIView):
    def get(self, request):
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
    permission_classes = [permissions.IsAuthenticated, IsSessionActive]

    def post(self, request):
        try:
            session = LoginSession.objects.get(user__id=request.user.id)
            session.delete()
            return Response({"msg": "You are Successfully Logged-out of the API"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UpdatePassword(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSessionActive]

    def post(self, request):
        user = request.user
        serializer = UpdatePasswordSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            new_password = serializer.validated_data
            user.set_password(new_password)
            user.save()
            session = LoginSession.objects.get(user__id=request.user.id)
            session.delete()
            return Response({"msg": "Your password has been updated Successfully"}, status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
