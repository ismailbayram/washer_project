from rest_framework.permissions import BasePermission


class IsAuthenticatedAndActivated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated \
                    and request.user.is_active)


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class HasGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or view.permission_groups is None:
            return True
        required_groups = view.permission_groups.get(view.action, None)
        if not required_groups:
            return True
        return any([self._is_in_group(request.user, group.value) for group in required_groups])

    def _is_in_group(self, user, group_name):
        return user.groups.filter(name=group_name).exists()
