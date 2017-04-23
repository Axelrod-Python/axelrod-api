from rest_framework import permissions


class AnonymousExceptDelete(permissions.BasePermission):

    def has_permission(self, request, view):
        # allow all POST requests
        if request.method == 'DELETE':
            return request.user.is_staff
        return True
