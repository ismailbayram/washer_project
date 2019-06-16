from django.urls import include, path

from rest_framework.routers import DefaultRouter

from users.resources.views import (UserViewSet, AuthView)

from api.views import get_swagger_view
schema_view = get_swagger_view(title='Washer Project API')

router = DefaultRouter()
router.register('users', UserViewSet, 'users')

app_name = 'api'

urlpatterns = [
    path('', include((router.urls, 'api'), namespace='api')),
    path('auth/', AuthView.as_view()),
    path('docs/', schema_view),
]
