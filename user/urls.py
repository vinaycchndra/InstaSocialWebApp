from django.urls import path, include
from .views import UserRegistrationView, LoginView, LogoutView, UpdatePassword
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('update-password/', UpdatePassword.as_view(), name='update-password'),

]
