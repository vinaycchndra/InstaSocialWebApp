from rest_framework.permissions import BasePermission
from user.models import LoginSession


class IsSessionActive(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        try:
            session = LoginSession.objects.get(user__id = user.id)
            if session.is_session_expired():
                return False
            else:
                return True
        except LoginSession.DoesNotExist:
            return False

