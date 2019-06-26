from django.urls import include, path

from rest_framework.routers import DefaultRouter

from users.resources.views import (UserViewSet, AuthView)

from cars.resources.views import (CarViewSet)

from address.resources.views import (CountryViewSet, CityViewSet,
                                     TownshipViewSet)
from stores.resources.views import StoreViewSet, StoreListViewSet

from cars.resources.views import (CarView)


from api.views import get_swagger_view
schema_view = get_swagger_view(title='Washer Project API')

router = DefaultRouter()
router.register('users', UserViewSet, 'users')

# addresses
router.register('countries', CountryViewSet, base_name='countries')
router.register('cities', CityViewSet, base_name='cities')
router.register('townships', TownshipViewSet, base_name='townships')
router.register('cars', CarViewSet, base_name='cars')

# stores
router.register('stores', StoreViewSet, base_name='my_stores')
router.register('stores_list', StoreListViewSet, base_name='stores')

app_name = 'api'

urlpatterns = [
    path('', include((router.urls, 'api'), namespace='router')),
    path('auth/', AuthView.as_view()),
    path('docs/', schema_view),
]
