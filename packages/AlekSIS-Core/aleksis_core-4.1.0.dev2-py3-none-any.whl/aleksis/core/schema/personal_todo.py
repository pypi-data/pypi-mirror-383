from django.core.exceptions import PermissionDenied

import graphene
from graphene_django import DjangoObjectType

from ..models import PersonalTodo
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    CalendarEventBatchCreateMixin,
    CalendarEventBatchPatchMixin,
)


class PersonalTodoType(DjangoObjectType):
    class Meta:
        model = PersonalTodo
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
            "completed",
            "parent",
        )

    timezone = graphene.String()
    recurrences = graphene.String()

    percent_complete = graphene.Int()


class PersonalTodoBatchCreateMutation(CalendarEventBatchCreateMixin, BaseBatchCreateMutation):
    class Meta:
        model = PersonalTodo
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
            "percent_complete",
            "completed",
            "parent",
        )
        field_types = {
            "timezone": graphene.String(),
            "recurrences": graphene.String(),
            "location": graphene.String(),
            "percent_complete": graphene.Int(),
        }
        optional_fields = ("description", "timezone", "recurrences")
        permissions = ("core.create_personaltodo_rule",)

    @classmethod
    def after_create_obj(cls, root, info, data, obj, input):  # noqa
        # Overwrite after_create_obj it is used by PermissionBatchCreateMixin
        if all([len(event.persons) == 0 and len(event.groups) == 0 for event in input]):
            perms = cls._meta.permissions
        else:
            perms = ("core.create_personaltodo_with_invitations_rule",)

        if not info.context.user.has_perms(perms, obj):
            raise PermissionDenied()

    @classmethod
    def before_mutate(cls, root, info, input):  # noqa
        super().before_mutate(root, info, input)
        for event in input:
            event["owner"] = info.context.user.person.id
        return input


class PersonalTodoBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = PersonalTodo
        permissions = ("core.delete_personaltodo_rule",)


class PersonalTodoBatchPatchMutation(CalendarEventBatchPatchMixin, BaseBatchPatchMutation):
    class Meta:
        model = PersonalTodo
        permissions = ("core.edit_personaltodo_rule",)
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
            "percent_complete",
            "completed",
            "parent",
        )
        field_types = {
            "timezone": graphene.String(),
            "recurrences": graphene.String(),
            "location": graphene.String(),
            "percent_complete": graphene.Int(),
        }
        optional_fields = ("description", "timezone", "recurrences")
