from rest_framework import serializers
from user.models import CustomUser
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(max_length=15, style={'input_type': 'password', 'write_only': True})

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if attrs.get('first_name') is None:
            raise serializers.ValidationError('First Name is Mandaroty')

        if attrs.get('last_name') is None:
            raise serializers.ValidationError('Last Name is Mandaroty')

        if attrs.get('date_of_birth') is None:
            raise serializers.ValidationError('Date of Birth is Mandaroty')

        if password2 != password:
            raise serializers.ValidationError('Password and Confirm Password are not same !!!')
        return attrs

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={'input_type': 'password', 'write_only': True})
    new_password1 = serializers.CharField(style={'input_type': 'password', 'write_only': True})
    new_password2 = serializers.CharField(style={'input_type': 'password', 'write_only': True})

    def validate(self, data):
        user = self.context.get('user')

        if check_password(data['old_password'], user.password):
            if data['new_password1'] != data['new_password2']:
                raise serializers.ValidationError('Passwords does not Match')
        else:
            raise serializers.ValidationError('Old Password is Incorrect')

        return data['new_password1']



