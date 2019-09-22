from rest_framework import serializers

from admin.dashboard.enums import GroupTimeType
from api.fields import EnumField

class GroupTimeSerializer(serializers.Serializer):
    group_time = EnumField(enum=GroupTimeType)
    start_date = serializers.DateTimeField(input_formats=['%d-%m-%Y', 'iso-8601'])
    end_date = serializers.DateTimeField(input_formats=['%d-%m-%Y', 'iso-8601'])
