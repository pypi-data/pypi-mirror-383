from graphene_django import DjangoObjectType

from ..models import Holiday
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    DjangoFilterMixin,
    PermissionsTypeMixin,
)


class HolidayType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = Holiday
        fields = ("id", "holiday_name", "date_start", "date_end")
        filter_fields = {
            "id": ["exact", "lte", "gte"],
            "holiday_name": ["icontains"],
            "date_start": ["exact", "lte", "gte"],
            "date_end": ["exact", "lte", "gte"],
        }


class HolidayBatchCreateMutation(BaseBatchCreateMutation):
    class Meta:
        model = Holiday
        permissions = ("core.create_holiday_rule",)
        only_fields = ("holiday_name", "date_start", "date_end")


class HolidayBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = Holiday
        permissions = ("core.delete_holiday_rule",)


class HolidayBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = Holiday
        permissions = ("core.edit_holiday_rule",)
        only_fields = ("id", "holiday_name", "date_start", "date_end")
