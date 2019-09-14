from django.urls import include, path
from rest_framework.routers import DefaultRouter

from admin.address.views import CityViewSet, CountryViewSet, TownshipViewSet
from admin.stores.views import StoreAdminViewSet
from admin.users.views import LoginView, UserViewSet

from api.views import get_swagger_view

schema_view = get_swagger_view(title='Washer Project API')

router = DefaultRouter()

# addresses
router.register('countries', CountryViewSet, base_name='countries')
router.register('cities', CityViewSet, base_name='cities')
router.register('townships', TownshipViewSet, base_name='townships')

# users
router.register('users', UserViewSet, 'users')

# stores
router.register('stores', StoreAdminViewSet, base_name='stores')


app_name = 'admin_api'

urlpatterns = [
    path('', include((router.urls, 'api'), namespace='router')),
    path('auth/', LoginView.as_view(), name="auth"),
]
