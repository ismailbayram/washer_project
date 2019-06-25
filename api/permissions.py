from rest_framework.permissions import BasePermission


class IsAuthenticatedAndActivated(BasePermission):
    # TODO: check is user Anonymous, return 411
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated \
                    and request.user.is_active)


class HasGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        required_groups = view.permission_groups.get(view.action, None)
        if required_groups is None:  # if ..{ action: [] } => only superusers
            return True
        return any([self._is_in_group(request.user, group.value) for group in required_groups])

    def _is_in_group(self, user, group_name):
        return user.groups.filter(name=group_name).exists()
