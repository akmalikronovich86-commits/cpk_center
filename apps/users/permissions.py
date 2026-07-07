from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsDirector(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'director'

class IsHead(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'head'

class IsMethodist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'methodist'

class IsLecturer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'lecturer'

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsDirectorOrHead(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['director', 'head']

class IsDirectorOrMethodist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['director', 'methodist']

class IsDirectorOrLecturer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['director', 'lecturer']

class IsOwnerOrDirector(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'director':
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        return obj == request.user

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        return False
