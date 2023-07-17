from rest_framework import serializers
from user.models import CustomUser


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
