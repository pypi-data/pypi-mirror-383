from django.contrib.contenttypes.models import ContentType

import graphene
from graphene_django import DjangoObjectType

from ..models import (
    Announcement,
    Group,
    Person,
)
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    PermissionsTypeMixin,
)
from .group import GroupType
from .person import PersonType


class AnnouncementType(PermissionsTypeMixin, DjangoObjectType):
    class Meta:
        model = Announcement
        fields = (
            "id",
            "datetime_start",
            "datetime_end",
            "title",
            "description",
            "priority",
            "is_global",
        )

    recipient_groups = graphene.List(GroupType)
    recipient_persons = graphene.List(PersonType)

    def resolve_recipient_groups(root, info, **kwargs):
        return root.get_recipients_for_model(Group)

    def resolve_recipient_persons(root, info, **kwargs):
        return root.get_recipients_for_model(Person)


class DisplayAnnouncementType(DjangoObjectType):
    class Meta:
        model = Announcement
        skip_registry = True
        fields = (
            "id",
            "datetime_start",
            "datetime_end",
            "title",
            "description",
            "priority",
        )


class AnnouncementBatchCreateMutation(BaseBatchCreateMutation):
    class Meta:
        model = Announcement
        permissions = ("core.create_announcement_rule",)
        only_fields = (
            "datetime_start",
            "datetime_end",
            "title",
            "description",
            "priority",
            "is_global",
        )
        custom_fields = {
            "recipient_groups": graphene.List(graphene.ID),
            "recipient_persons": graphene.List(graphene.ID),
        }

    @classmethod
    def after_mutate(cls, root, info, input, created_objs, return_data):  # noqa
        """Create AnnouncementRecipients"""
        for spec, obj in zip(input, created_objs):
            for group in spec.recipient_groups:
                obj.recipients.create(recipient=Group.objects.get(id=group))
            for person in spec.recipient_persons:
                obj.recipients.create(recipient=Person.objects.get(id=person))


class AnnouncementBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = Announcement
        permissions = ("core.delete_announcement_rule",)

    @classmethod
    def before_save(cls, root, info, ids, qs_to_delete):
        """Delete AnnouncementRecipients"""
        for announcement in qs_to_delete:
            # Copied from forms.py
            announcement.recipients.all().delete()


class AnnouncementBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = Announcement
        permissions = ("core.edit_announcement_rule",)
        only_fields = (
            "id",
            "datetime_start",
            "datetime_end",
            "title",
            "description",
            "priority",
            "is_global",
        )
        custom_fields = {
            "recipient_groups": graphene.List(graphene.ID),
            "recipient_persons": graphene.List(graphene.ID),
        }

    @classmethod
    def after_mutate(cls, root, info, input, updated_objs, return_data):  # noqa
        """Update AnnouncementRecipients"""

        def delete_announcement_recipients_of_model(announcement, model):
            # Del & then recreate
            ct = ContentType.objects.get_for_model(model)
            announcement.recipients.filter(content_type=ct).delete()

        for spec, obj in zip(input, updated_objs):
            if spec.recipient_groups:
                delete_announcement_recipients_of_model(obj, Group)
                for group in spec.recipient_groups:
                    obj.recipients.create(recipient=Group.objects.get(id=group))

            if spec.recipient_persons:
                delete_announcement_recipients_of_model(obj, Person)
                for person in spec.recipient_persons:
                    obj.recipients.create(recipient=Person.objects.get(id=person))
