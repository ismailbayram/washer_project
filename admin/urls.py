from django.urls import include, path
from rest_framework.routers import DefaultRouter

from admin.address.views import (CityViewSet, CountryViewSet,
                                 TownshipViewSet)

from api.views import get_swagger_view
from cars.resources.views import CarViewSet
from notifications.resources.views import NotificationViewSet
from products.resources.views import ProductListViewSet, ProductViewSet
from reservations.resources.views import (CommentListViewSet,
                                          CustomerReservationViewSet,
                                          StoreReservationViewSet)
from admin.stores.views import StoreAdminViewSet
from users.resources.views import (AuthView, SmsVerify, UserViewSet,
                                   WorkerProfileViewSet)
from search.resources.views import (ReservationSearchView,
                                    StoreSearchView)

schema_view = get_swagger_view(title='Washer Project API')

router = DefaultRouter()

# addresses
router.register('countries', CountryViewSet, base_name='countries')
router.register('cities', CityViewSet, base_name='cities')
router.register('townships', TownshipViewSet, base_name='townships')

# stores
router.register('stores', StoreAdminViewSet, base_name='stores')


app_name = 'admin_api'

urlpatterns = [
    path('', include((router.urls, 'api'), namespace='router')),
]
