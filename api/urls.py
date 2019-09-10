from django.urls import include, path
from rest_framework.routers import DefaultRouter

from address.resources.views import (CityViewSet, CountryViewSet,
                                     TownshipViewSet)

from api.views import get_swagger_view
from baskets.resources.views import BasketViewSet, CampaignViewSet
from cars.resources.views import CarViewSet
from notifications.resources.views import NotificationViewSet
from products.resources.views import ProductListViewSet, ProductViewSet
from reservations.resources.views import (CommentListViewSet,
                                          CustomerReservationViewSet,
                                          StoreReservationViewSet)
from stores.resources.views import StoreViewSet, StoreDetailView
from users.resources.views import (AuthView, SmsVerify,
                                   WorkerProfileViewSet)
from search.resources.views import (ReservationSearchView,
                                    StoreSearchView)

schema_view = get_swagger_view(title='Washer Project API')

router = DefaultRouter()
router.register('workers', WorkerProfileViewSet, 'workers')

# addresses
router.register('countries', CountryViewSet, base_name='countries')
router.register('cities', CityViewSet, base_name='cities')
router.register('townships', TownshipViewSet, base_name='townships')

# stores
router.register('stores', StoreViewSet, base_name='my_stores')

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
router.register('campaigns', CampaignViewSet, base_name='campaigns')

# reservations
router.register('my_reservations', StoreReservationViewSet, base_name='my_reservations')  # for store
router.register('reservations', CustomerReservationViewSet, base_name='reservations')  # for customers
router.register('comments', CommentListViewSet, base_name='comments')

# notifications
router.register('notifications', NotificationViewSet, base_name='notifications')

app_name = 'api'

urlpatterns = [
    path('reservation_search/', ReservationSearchView.as_view(), name='reservation_search'),  # for everyone
    path('store_search/', StoreSearchView.as_view(), name='store_search'),  # for everyone
    path('store/<int:pk>/', StoreDetailView.as_view(), name='store_detail'),  # for everyone
    path('basket/', basket_view, name='basket'),
    path('', include((router.urls, 'api'), namespace='router')),
    path('auth/', AuthView.as_view(), name="auth"),
    path('sms_verify/', SmsVerify.as_view(), name="sms_verify"),
    path('docs/', schema_view),
]
