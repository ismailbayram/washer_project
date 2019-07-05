from django.urls import include, path

from rest_framework.routers import DefaultRouter

from users.resources.views import (UserViewSet, AuthView, WorkerProfileViewSet)
from cars.resources.views import (CarViewSet)
from address.resources.views import (CountryViewSet, CityViewSet,
                                     TownshipViewSet)
from stores.resources.views import StoreViewSet, StoreListViewSet

from api.views import get_swagger_view
schema_view = get_swagger_view(title='Washer Project API')

router = DefaultRouter()
router.register('users', UserViewSet, 'users')
router.register('workers', WorkerProfileViewSet, 'workers')

# addresses
router.register('countries', CountryViewSet, base_name='countries')
router.register('cities', CityViewSet, base_name='cities')
router.register('townships', TownshipViewSet, base_name='townships')

# stores
router.register('stores', StoreViewSet, base_name='my_stores')
router.register('stores_list', StoreListViewSet, base_name='stores')

# cars
router.register('cars', CarViewSet, base_name='cars')

app_name = 'api'

urlpatterns = [
    path('', include((router.urls, 'api'), namespace='router')),
    path('auth/', AuthView.as_view()),
    path('docs/', schema_view),
]
