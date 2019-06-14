from django.urls import include, path

from rest_framework.routers import DefaultRouter

from users.resources.views import (UserViewSet, AuthView)


# TODO: prevent /api/v1/ :GET
router = DefaultRouter()
router.register('users', UserViewSet)

app_name = 'api'

urlpatterns = [
    path('auth/', AuthView.as_view()),
    path('', include(router.urls)),
]
