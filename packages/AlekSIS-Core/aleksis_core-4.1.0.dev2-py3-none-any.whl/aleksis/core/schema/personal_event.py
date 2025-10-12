from django.core.exceptions import PermissionDenied

import graphene
from graphene_django import DjangoObjectType

from ..models import PersonalEvent
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    CalendarEventBatchCreateMixin,
    CalendarEventBatchPatchMixin,
)


class PersonalEventType(DjangoObjectType):
    class Meta:
        model = PersonalEvent
        fields = (
            "id",
            "title",
            "description",
            "location",
            "datetime_start",
            "datetime_end",
            "date_start",
            "date_end",
            "owner",
            "persons",
            "groups",
        )

    timezone = graphene.String()
    recurrences = graphene.String()


class PersonalEventBatchCreateMutation(CalendarEventBatchCreateMixin, BaseBatchCreateMutation):
    class Meta:
        model = PersonalEvent
        only_fields = (
            "title",
            "description",
            "location",
            "datetime_start",
            "datetime_end",
            "timezone",
            "date_start",
            "date_end",
            "recurrences",
            "persons",
            "groups",
        )
        field_types = {
            "timezone": graphene.String(),
            "recurrences": graphene.String(),
            "location": graphene.String(),
        }
        optional_fields = ("description", "timezone", "recurrences")
        permissions = ("core.create_personal_event_rule",)

    @classmethod
    def after_create_obj(cls, root, info, data, obj, input):  # noqa
        # Overwrite after_create_obj it is used by PermissionBatchCreateMixin
        if all([len(event.persons) == 0 and len(event.groups) == 0 for event in input]):
            perms = cls._meta.permissions
        else:
            perms = ("core.create_personal_event_with_invitations_rule",)

        if not info.context.user.has_perms(perms, obj):
            raise PermissionDenied()

    @classmethod
    def before_mutate(cls, root, info, input):  # noqa
        super().before_mutate(root, info, input)
        for event in input:
            event["owner"] = info.context.user.person.id
        return input


class PersonalEventBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = PersonalEvent
        permissions = ("core.delete_personal_event_rule",)


class PersonalEventBatchPatchMutation(CalendarEventBatchPatchMixin, BaseBatchPatchMutation):
    class Meta:
        model = PersonalEvent
        permissions = ("core.edit_personal_event_rule",)
        only_fields = (
            "id",
            "title",
            "description",
            "location",
            "datetime_start",
            "datetime_end",
            "timezone",
            "date_start",
            "date_end",
            "recurrences",
            "persons",
            "groups",
        )
        field_types = {
            "timezone": graphene.String(),
            "recurrences": graphene.String(),
            "location": graphene.String(),
        }
        optional_fields = ("description", "timezone", "recurrences")
