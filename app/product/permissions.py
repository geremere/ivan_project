from rest_framework import permissions
from rest_framework.permissions import IsAdminUser


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        IsAdminUser
        if request.