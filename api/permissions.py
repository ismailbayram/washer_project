from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedAndActivated(BasePermission):
    # TODO: check is user is_active, return 411
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated \
                    and request.user.is_active)


class HasGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        required_groups = view.permission_groups.get(view.action, None)
        if required_groups is None:  # if ..{ action: [] } => only staffs
            return True
        return any([self._is_in_group(request.user, group.value) for group in required_groups])

    def _is_in_group(self, user, group_name):
        return user.groups.filter(name=group_name).exists()


class IsCustomerOrReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if (request.user.customer_profile == obj.customer_profile) or request.user.is_staff:
            return True
        return False


class IsWasherOrReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if (request.user.is_authenticated and request.user.washer_profile == obj.washer_profile) or \
                request.user.is_staff:
            return True
        return False
