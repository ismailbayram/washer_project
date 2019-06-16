from rest_framework.schemas import generators


class EndpointEnumerator(generators.EndpointEnumerator):
    def __init__(self, patterns=None, urlconf=None):
        super(EndpointEnumerator, self).__init__(patterns=patterns,
                                                 urlconf=urlconf)

    def get_allowed_methods(self, callback):
        """
        Return a list of the valid HTTP methods for this endpoint.
        """
        if hasattr(callback, 'actions'):
            actions = set(callback.actions)
            http_method_names = set(callback.cls.http_method_names)
            if 'options' in http_method_names:
                actions.update({'options'})
            methods = [method.upper() for method in actions & http_method_names]
        else:
            methods = callback.cls().allowed_methods

        return [method for method in methods if method not in 'HEAD']


class SchemaGenerator(generators.SchemaGenerator):
    default_mapping = {
        'get': 'retrieve',
        'post': 'create',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
        'options': 'options'
    }
    endpoint_inspector_cls = EndpointEnumerator

    def __init__(self, title=None, url=None, description=None,
                 patterns=None, urlconf=None):
        super(SchemaGenerator, self).__init__(title=title, url=url,
                                              description=description,
                                              patterns=patterns,
                                              urlconf=urlconf)

    def get_keys(self, subpath, method, view):
        """
        Return a list of keys that should be used to layout a link within
        the schema document.

        /users/                   ("users", "list"), ("users", "create")
        /users/{pk}/              ("users", "read"), ("users", "update"), ("users", "delete")
        /users/enabled/           ("users", "enabled")  # custom viewset list action
        /users/{pk}/star/         ("users", "star")     # custom viewset detail action
        /users/{pk}/groups/       ("users", "groups", "list"), ("users", "groups", "create")
        /users/{pk}/groups/{pk}/  ("users", "groups", "read"), ("users", "groups", "update"), ("users", "groups", "delete")
        """
        if hasattr(view, 'action'):
            # Viewsets have explicitly named actions.
            action = view.action
        else:
            # Views have no associated action,
            # so we determine one from the method.
            if generators.is_list_view(subpath, method, view):
                action = 'list'
            else:
                action = self.default_mapping[method.lower()]

        named_path_components = [
            component for component
            in subpath.strip('/').split('/')
            if '{' not in component
        ]

        if generators.is_custom_action(action):
            # Custom action, eg "/users/{pk}/activate/", "/users/active/"
            if view.action_map is not None and len(view.action_map) > 1:
                action = self.default_mapping[method.lower()]
                if action in self.coerce_method_names:
                    action = self.coerce_method_names[action]
                return named_path_components + [action]
            else:
                return named_path_components[:-1] + [action]

        if action in self.coerce_method_names:
            action = self.coerce_method_names[action]

        # Default action, eg "/users/", "/users/{pk}/"
        return named_path_components + [action]

    def has_view_permissions(self, path, method, view):
        return True
