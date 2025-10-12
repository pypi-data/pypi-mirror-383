from django.core.exceptions import PermissionDenied

import graphene
from graphene_django import DjangoObjectType

from ..models import AvailabilityEvent, AvailabilityType
from ..util.core_helpers import has_person
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    CalendarEventBatchCreateMixin,
    CalendarEventBatchPatchMixin,
    DjangoFilterMixin,
    PermissionsTypeMixin,
)


class AvailabilityTypeType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = AvailabilityType
        fields = (
            "id",
            "name",
            "short_name",
            "description",
            "public",
            "color",
            "free",
        )
        filter_fields = {
            "id": ["exact", "lte", "gte"],
            "title": ["icontains"],
            "short_name": ["icontains"],
            "description": ["icontains"],
            "public": ["exact"],
            "free": ["exact"],
            "color": ["icontains"],
        }


class AvailabilityTypeBatchCreateMutation(BaseBatchCreateMutation):
    class Meta:
        model = AvailabilityType
        permissions = ("core.create_availability_type_rule",)
        only_fields = (
            "name",
            "short_name",
            "description",
            "public",
            "color",
            "free",
        )
        optional_fields = ("description",)


class AvailabilityTypeBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = AvailabilityType
        permissions = ("core.delete_availability_type_rule",)


class AvailabilityTypeBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = AvailabilityType
        permissions = ("core.edit_availability_type_rule",)
        only_fields = (
            "id",
            "name",
            "short_name",
            "description",
            "public",
            "color",
            "free",
        )
        optional_fields = ("description",)


class AvailabilityEventType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = AvailabilityEvent
        fields = (
            "id",
            "title",
            "person",
            "description",
            "availability_type",
            "date_start",
            "date_end",
            "datetime_start",
            "datetime_end",
        )
        filter_fields = {
            "id": ["exact", "lte", "gte"],
            "title": ["icontains"],
            "person": ["exact"],
            "description": ["icontains"],
            "date_start": ["exact", "lte", "gte"],
            "date_end": ["exact", "lte", "gte"],
            "datetime_start": ["exact", "lte", "gte"],
            "datetime_end": ["exact", "lte", "gte"],
            "recurrences": ["exact"],
            "timezone": ["exact"],
        }
        convert_choices_to_enum = False

    timezone = graphene.String()
    recurrences = graphene.String()


class AvailabilityEventBatchCreateMutation(CalendarEventBatchCreateMixin, BaseBatchCreateMutation):
    class Meta:
        model = AvailabilityEvent
        permissions = ("core.create_availability_event_rule",)
        only_fields = (
            "title",
            "description",
            "availability_type",
            "date_start",
            "date_end",
            "datetime_start",
            "datetime_end",
            "timezone",
            "recurrences",
        )
        optional_fields = (
            "description",
            "timezone",
        )
        field_types = {
            "timezone": graphene.String(),
            "recurrences": graphene.String(),
        }

    # This has to be done in such an inconvenient way since the
    # before_save method of the batch create mutation is indeed
    # not run before the save
    @classmethod
    def before_mutate(cls, root, info, input):  # noqa
        super().before_mutate(root, info, input)
        if has_person(info.context.user):
            for event in input:
                event["person"] = info.context.user.person.id
            return input
        raise PermissionDenied()


class AvailabilityEventBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = AvailabilityEvent
        permissions = ("core.delete_availability_event_rule",)


class AvailabilityEventBatchPatchMutation(CalendarEventBatchPatchMixin, BaseBatchPatchMutation):
    class Meta:
        model = AvailabilityEvent
        permissions = ("core.edit_availability_event_rule",)
        only_fields = (
            "id",
            "title",
            "description",
            "availability_type",
            "date_start",
            "date_end",
            "datetime_start",
            "datetime_end",
            "timezone",
            "recurrences",
        )
        optional_fields = ("description", "timezone")
        field_types = {
            "recurrences": graphene.String(),
            "timezone": graphene.String(),
        }
