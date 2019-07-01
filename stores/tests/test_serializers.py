from django.test import TestCase
from rest_framework.exceptions import ValidationError

from stores.resources.serializers import DaySerializer, WeekSerializer, ConfigSerializer


class StoreSerializersTest(TestCase):
    def test_day_serializer(self):
        data = {}
        serializer = DaySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data['start'], None)
        self.assertEqual(serializer.validated_data['end'], None)

        data = {"start": None, "end": "18:00"}
        with self.assertRaises(ValidationError):
            serializer = DaySerializer(data=data)
            serializer.is_valid(raise_exception=True)

        data = {"start": "21:00", "end": "18:00"}
        with self.assertRaises(ValidationError):
            serializer = DaySerializer(data=data)
            serializer.is_valid(raise_exception=True)

        data = {"start": "09", "end": "18:00"}
        with self.assertRaises(ValidationError):
            serializer = DaySerializer(data=data)
            serializer.is_valid(raise_exception=True)

        data = {"start": "09:00", "end": "1800"}
        with self.assertRaises(ValidationError):
            serializer = DaySerializer(data=data)
            serializer.is_valid(raise_exception=True)

        data = {"start": "09:00", "end": "18:00"}
        serializer = DaySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data['start'], "09:00")
        self.assertEqual(serializer.validated_data['end'], "18:00")

    def test_week_serializer(self):
        data = {
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
            "sunday": {
                "start": None,
                "end": None
            }
        }

        serializer = WeekSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

        data.update({
            'saturday': {"start": "09:00", "end": "18:00"}
        })

    def test_config_serializer(self):
        data = {
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
                    "start": "16:00",
                    "end": "18:00"
                },
                "sunday": {
                    "start": "09:00",
                    "end": "18:00"
                }
            }
        }
        serializer = ConfigSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

        data['reservation_hours'].update({
            "saturday": {
                "start": "08:00",
                "end": "19:00"
            },
            "sunday": {
                "start": None,
                "end": None
            }
        })
        serializer = ConfigSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

        data['reservation_hours'].update({
            "saturday": {
                "start": "09:00",
                "end": "19:00"
            }
        })
        serializer = ConfigSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

        data['reservation_hours'].update({
            "saturday": {
                "start": "09:00",
                "end": "18:00"
            }
        })
        serializer = ConfigSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.assertEqual(data['reservation_hours'], serializer.validated_data['reservation_hours'])
        self.assertEqual(data['opening_hours'], serializer.validated_data['opening_hours'])
