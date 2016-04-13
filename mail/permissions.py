from rest_framework import permissions
from .models import Account


class IsAccountOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, account):
        if request.user:
            return account == request.user
        return False


class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_admin





