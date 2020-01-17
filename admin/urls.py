from django.urls import include, path
from rest_framework.routers import DefaultRouter

from admin.address.views import CityViewSet, CountryViewSet, TownshipViewSet
from admin.stores.views import StoreAdminViewSet
from admin.users.views import LoginView, UserViewSet, WorkerJobLogViewSet
from admin.reservations.views import ReservationCancellationAdminViewSet, \
                                     ReservationAdminViewSet
from admin.cars.views import CarAdminViewSet
from admin.dashboard.views import DashboardViewSet
from admin.campaigns.views import CampaignAdminViewSet
from admin.products.views import ProductPriceAdminViewSet

from api.views import get_swagger_view

schema_view = get_swagger_view(title='Washer Project API')

router = DefaultRouter()

# addresses
router.register('countries', CountryViewSet, base_name='countries')
router.register('cities', CityViewSet, base_name='cities')
router.register('townships', TownshipViewSet, base_name='townships')

# dashboard
router.register('dashboard', DashboardViewSet, base_name='dashboard')

# users
router.register('users', UserViewSet, 'users')

# stores
router.register('stores', StoreAdminViewSet, base_name='stores')

# cars
router.register('cars', CarAdminViewSet, base_name='cars')

# reservations
router.register('cancellation_reasons', ReservationCancellationAdminViewSet, base_name='cancellation_reasons')
router.register('reservations', ReservationAdminViewSet, base_name='reservations')

# campaigns
router.register('campaigns', CampaignAdminViewSet, base_name='campaigns')

# products
router.register('product_prices', ProductPriceAdminViewSet, base_name='product_prices')

# worker job log
router.register('worker_job_log', WorkerJobLogViewSet, base_name='worker_job_log')

app_name = 'admin_api'

urlpatterns = [
    path('', include((router.urls, 'api'), namespace='router')),
    path('auth/', LoginView.as_view(), name='auth'),
]
