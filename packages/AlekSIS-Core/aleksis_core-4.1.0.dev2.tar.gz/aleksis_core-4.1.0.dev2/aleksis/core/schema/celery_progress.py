from django.contrib.messages.constants import DEFAULT_TAGS

import graphene
from django_celery_results.models import TaskResult
from graphene import ObjectType
from graphene_django import DjangoObjectType

from ..models import TaskUserAssignment


class CeleryProgressMessage(ObjectType):
    message = graphene.String(required=True)
    level = graphene.Int(required=True)
    tag = graphene.String(required=True)

    def resolve_message(root, info, **kwargs):
        return root[1]

    def resolve_level(root, info, **kwargs):
        return root[0]

    def resolve_tag(root, info, **kwargs):
        return DEFAULT_TAGS.get(root[0], "info")


class CeleryProgressAdditionalButtonType(ObjectType):
    title = graphene.String(required=True)
    url = graphene.String(required=True)
    icon = graphene.String()


class CeleryProgressMetaType(DjangoObjectType):
    additional_button = graphene.Field(CeleryProgressAdditionalButtonType, required=False)

    class Meta:
        model = TaskUserAssignment
        fields = (
            "id",
            "title",
            "back_url",
            "progress_title",
            "error_message",
            "success_message",
            "redirect_on_success_url",
            "additional_button",
        )

    @classmethod
    def get_queryset(cls, queryset, info, perm="core.view_progress_rule"):
        return super().get_queryset(queryset, info, perm)

    def resolve_additional_button(root, info, **kwargs):
        if not root.additional_button_title or not root.additional_button_url:
            return None
        return {
            "title": root.additional_button_title,
            "url": root.additional_button_url,
            "icon": root.additional_button_icon,
        }


class CeleryProgressProgressType(ObjectType):
    current = graphene.Int()
    total = graphene.Int()
    percent = graphene.Float()


class CeleryProgressType(graphene.ObjectType):
    state = graphene.String()
    complete = graphene.Boolean()
    success = graphene.Boolean()
    progress = graphene.Field(CeleryProgressProgressType)
    messages = graphene.List(CeleryProgressMessage)
    meta = graphene.Field(CeleryProgressMetaType)

    def resolve_messages(root, info, **kwargs):  # noqa
        if root["complete"] and isinstance(root["result"], list):
            return root["result"]
        return root["progress"].get("messages", [])


class CeleryTaskResultType(DjangoObjectType):
    class Meta:
        model = TaskResult
        fields = (
            "task_name",
            "task_id",
            "date_done",
            "status",
        )


class CeleryProgressFetchedMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    celery_progress = graphene.Field(CeleryProgressType)

    def mutate(root, info, id, **kwargs):  # noqa: A002
        task = TaskUserAssignment.objects.get(id=id)

        if not info.context.user.has_perm("core.view_progress_rule", task):
            return None
        task.result_fetched = True
        task.save()
        progress = task.get_progress_with_meta()
        return CeleryProgressFetchedMutation(celery_progress=progress)
