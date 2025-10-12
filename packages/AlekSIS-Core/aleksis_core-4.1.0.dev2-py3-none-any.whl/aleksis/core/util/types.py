from django.utils.encoding import force_str

from graphene import Scalar
from graphene_django.converter import convert_django_field
from graphql import GraphQLError, StringValueNode, print_ast
from timezone_field import TimeZoneField
from timezone_field.backends import TimeZoneNotFoundError, get_tz_backend, zoneinfo


class TimeZone(Scalar):
    """
    The `TimeZone` scalar type represents a TimeZone that is accepted by django-timezone-field.

    Based on https://github.com/mfogel/django-timezone-field/blob/main/timezone_field/rest_framework.py
    and https://docs.graphene-python.org/en/latest/_modules/graphene/types/datetime/
    """

    @staticmethod
    def serialize(tz):
        return str(tz)

    @classmethod
    def parse_literal(cls, node, _variables=None):
        if not isinstance(node, StringValueNode):
            raise GraphQLError(f"TimeZone is not a string: {print_ast(node)}")
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        if isinstance(value, zoneinfo.zoneinfo.ZoneInfo):
            return value
        if not isinstance(value, str):
            raise GraphQLError(f"TimeZone is not a string: {repr(value)}")

        data_str = force_str(value)
        try:
            return get_tz_backend(use_pytz=False).to_tzobj(data_str)
        except TimeZoneNotFoundError as e:
            raise GraphQLError(f"Invalid timezone: {data_str}") from e


def setup_types():
    @convert_django_field.register(TimeZoneField)
    def convert_timezone_field(field, registry=None):
        return TimeZone(description=field.help_text, required=not field.null)
