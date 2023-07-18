from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, BaseUserManager
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta, datetime
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password, password2, **kwargs):
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_superuser', False)

        if not email:
            raise ValueError('Please provide email address')

        if kwargs.get('is_superuser') is True:
            raise ValueError('A normal user can not be assigned the role of superuser')
        if kwargs.get('is_staff') is True:
            raise ValueError('A normal user can not be assigned the role of staff person')
        if kwargs.get('is_active') is False:
            raise ValueError('A user must be active in order to use the application')

        if password is None:
            raise ValueError('Please Provide a Valid Password !!!')

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_superuser', True)

        if kwargs.get('is_superuser') is not True:
            raise ValueError('A superuser must be assigned to is_superuser=True')
        if kwargs.get('is_staff') is not True:
            raise ValueError('A superuser must be assigned to is_superuser=True')

        del kwargs['is_superuser'], kwargs['is_staff']
        superuser = self.create_user(email, first_name, last_name, password, password2=None,**kwargs)
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.save()
        return superuser


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateField(auto_now_add=True)

    # required fields to make user model work with admin rest is taken care by
    # PermissionMixins class

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_tokens_for_user(self):
        refresh = RefreshToken.for_user(self)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class LoginSession(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    login_start = models.DateTimeField(auto_now_add=True)

    def is_session_expired(self):
        login_object_end = self.login_start + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
        current_time = datetime.now(self.login_start.tzinfo)
        return login_object_end < current_time

    def __str__(self):
        return self.user.email





