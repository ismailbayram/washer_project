from django.urls import include, path
from rest_framework.routers import DefaultRouter

from address.resources.views import (CityViewSet, CountryViewSet,
                                     TownshipViewSet)
from api.views import get_swagger_view
from baskets.resources.views import BasketViewSet
from cars.resources.views import CarViewSet
from products.resources.views import ProductListViewSet, ProductViewSet
from reservations.resources.views import ReservationViewSet
from stores.resources.views import StoreListViewSet, StoreViewSet
from users.resources.views import (AuthView, SmsVerify, UserViewSet,
                                   WorkerProfileViewSet)

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

# products
router.register('products', ProductViewSet, base_name='my_products')
router.register('product_list', ProductListViewSet, base_name='products')

# basket
basket_view = BasketViewSet.as_view({
    'get': 'view_basket',
    'post': 'add_item',
    'delete': 'delete_item',
})

# reservations
router.register('reservations', ReservationViewSet, base_name='reservations')

app_name = 'api'

urlpatterns = [
    path('', include((router.urls, 'api'), namespace='router')),
    path('basket/', basket_view, name='basket'),
    path('auth/', AuthView.as_view()),
    path('sms_verify/', SmsVerify.as_view()),
    path('docs/', schema_view),
]
