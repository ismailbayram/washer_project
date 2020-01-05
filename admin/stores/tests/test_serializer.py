import datetime

from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from admin.stores.serializers import StoreAdminDetailedSerializer
from base.test import BaseTestViewMixin
from products.models import Product
from products.service import ProductService
from reservations.enums import ReservationStatus
from reservations.service import CommentService, ReservationService
from reservations.resources.serializers import CommentSerializer


class StoreSerializerTest(BaseTestViewMixin, TestCase):
    def setUp(self):
        self.init_users()
        self.address = mommy.make('address.Address')
        self.address2 = mommy.make('address.Address')
        self.store = mommy.make(
            'stores.Store',
            washer_profile=self.washer_profile,
            is_approved=True,
            is_active=False,
            address=self.address,
            latitude=35,
            longitude=34,
            phone_number="+905382451188",
            tax_office="1",
            tax_number="2",
            name="k",
        )
        self.store.config = {
            "opening_hours": {
                "monday": {
                    "start": "09:00",
                    "end": "20:00"
                },
                "tuesday": {
                    "start": "09:00",
                    "end": "20:00"
                },
                "wednesday": {
                    "start": "09:00",
                    "end": "20:00"
                },
                "thursday": {
                    "start": "09:00",
                    "end": "20:00"
                },
                "friday": {
                    "start": "09:00",
                    "end": "20:00"
                },
                "saturday": {
                    "start": "09:00",
                    "end": "18:00"
                },
                "sunday": {
                    "start": None,
                    "end": None
                }
            },
            "reservation_hours": {
                "monday": {
                    "start": None,
                    "end": None
                },
                "tuesday": {
                    "start": None,
                    "end": None
                },
                "wednesday": {
                    "start": None,
                    "end": None
                },
                "thursday": {
                    "start": "09:00",
                    "end": "13:00"
                },
                "friday": {
                    "start": "19:15",
                    "end": "20:00"
                },
                "saturday": {
                    "start": "16:00",
                    "end": "19:00"
                },
                "sunday": {
                    "start": None,
                    "end": None
                }
            }
        }
        self.store.save()

        ProductService().create_primary_product(self.store)
        self.product = ProductService().update_product(
            product=Product.objects.last(),
            name="Arac Parfumu",
            period=45,
        )

        dt = datetime.datetime(2019, 7, 18, 5, 51)  # Thursday
        ReservationService().create_day_from_config(self.store, dt, self.product.period)

        reservation = ReservationService()._create_reservation(
            self.store, timezone.now(), 40
        )
        reservation.status = ReservationStatus.completed
        reservation.save()

        # print(reservation.rating)
        self.comment1 = CommentService().comment(
            rating=10, comment="naber", reservation=reservation
        )

        reservation = ReservationService()._create_reservation(
            self.store, timezone.now(), 40
        )
        reservation.status = ReservationStatus.completed
        reservation.save()
        self.comment2 = CommentService().comment(
            rating=8, comment="iyi", reservation=reservation
        )

    def _recursive_equal_control(self, comming_data, expected_data, date_fields):
        """
        :param coming_data: Dict
        :param expected_data: Dict
        :date_fields: List
        it checks comming data and expected data is equal or not

        data_fields for the datetime checking. the comming part and expected
        part has a minimal diffrences (the strings are different). so that
        kind of field, this function translate that fields to datetime and
        check the difference has 60 second or not
        """
        for expected_key, expected_val in expected_data.items():
            if expected_key == 'last_comments':
                self._recursive_equal_control(
                    comming_data[expected_key][1], CommentSerializer(self.comment1).data, []
                )

                self._recursive_equal_control(
                    comming_data[expected_key][0], CommentSerializer(self.comment2).data, []
                )

            elif expected_key not in date_fields:
                if isinstance(expected_val, dict):
                    self._recursive_equal_control(
                        comming_data[expected_key],
                        expected_val,
                        date_fields
                    )
                else:
                    self.assertEqual(expected_val, comming_data[expected_key])
            else:
                comming_time = datetime.datetime.strptime(
                    comming_data[expected_key],
                    "%Y-%m-%dT%H:%M:%S.%f%z"
                )
                self.assertAlmostEqual(
                    comming_time, expected_val, delta=datetime.timedelta(
                        seconds=60)
                )

    def test_store_admin_detailed_serializer(self):
        expected_data = {
            # "pk": 3947,
            "name": "k",
            "washer_profile": {
                # "pk": 2001,
                'user': {
                    # 'pk': 22920,
                    'date_joined': timezone.now(),
                    'last_login': timezone.now(),
                    'first_name': 'Washer 1',
                    'last_name': 'WashLast',
                    'phone_number': '555333',
                    'is_active': True,
                    'is_customer': False,
                    'is_washer': True,
                    'is_worker': False
                }
            },
            "phone_number": "+905382451188",
            "latitude": 35,
            "longitude": 34,
            "tax_office": "1",
            "tax_number": "2",
            "rating": 9,
            "is_active": False,
            "is_approved": True,
            "weekly_reservation_count": 10,
            "created_date":  timezone.now(),
            "modified_date": timezone.now(),
            "images": [],
            "logo": None,
            "worker_profiles": [],
            "last_comments": [],
            "period": 45,
            'payment_options': {
                'credit_card': False,
                'cash': True
            }
        }

        comming_data = StoreAdminDetailedSerializer(self.store).data
        dates = ['date_joined', 'last_login', 'created_date', 'modified_date']

        self._recursive_equal_control(comming_data, expected_data, dates)

        self.store.config["reservation_hours"]["monday"] = {
            "start": "10:00",
            "end": "12:00",
        }
        self.store.save()
        expected_data["weekly_reservation_count"] = 12
        comming_data = StoreAdminDetailedSerializer(self.store).data
        self._recursive_equal_control(comming_data, expected_data, dates)
