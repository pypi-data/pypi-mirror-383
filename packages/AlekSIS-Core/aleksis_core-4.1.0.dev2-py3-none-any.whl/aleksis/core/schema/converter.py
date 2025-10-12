from colorfield.fields import ColorField
from graphene_django.converter import convert_django_field, get_django_field_description

from aleksis.core.fields import WeekdayField


@convert_django_field.register(ColorField)
def color_field_converter(field, registry=None):
    from .base import Color

    return Color(description=get_django_field_description(field), required=not field.null)


@convert_django_field.register(WeekdayField)
def weekday_field_converter(field, registry=None):
    from .base import Weekday

    return Weekday(description=get_django_field_description(field), required=not field.null)
