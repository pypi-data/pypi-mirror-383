from django.core.exceptions import PermissionDenied

import graphene
from graphene_django import DjangoObjectType

from aleksis.core.util.core_helpers import has_person

from ..models import Notification


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = [
            "id",
            "sender",
            "recipient",
            "title",
            "description",
            "link",
            "icon",
            "send_at",
            "read",
            "sent",
            "created",
            "modified",
        ]
        convert_choices_to_enum = False

    @staticmethod
    def resolve_recipient(root, info, **kwargs):
        if info.context.user.has_perm("core.view_person_rule", root.recipient):
            return root.recipient
        return None


class MarkNotificationReadMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()  # noqa

    notification = graphene.Field(NotificationType)

    @classmethod
    def mutate(cls, root, info, id):  # noqa
        notification = Notification.objects.get(pk=id)

        if not info.context.user.has_perm("core.mark_notification_as_read_rule", notification):
            raise PermissionDenied()
        notification.read = True
        notification.save()

        return MarkNotificationReadMutation(notification=notification)


class MarkAllNotificationsReadMutation(graphene.Mutation):
    notifications = graphene.List(NotificationType)

    @classmethod
    def mutate(cls, root, info):  # noqa
        if not has_person(info.context.user):
            raise PermissionDenied()

        notifications = Notification.objects.filter(recipient=info.context.user.person, read=False)
        notifications.update(read=True)

        return MarkAllNotificationsReadMutation(notifications=notifications)
