import random

from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet

import graphene
from graphene.types.objecttype import ObjectType
from graphene_django.registry import get_global_registry

from aleksis.core.models import (
    DashboardWidget,
    DashboardWidgetInstance,
)
from aleksis.core.schema.base import (
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    BaseObjectType,
    DjangoFilterMixin,
    PermissionsTypeMixin,
)
from aleksis.core.util.core_helpers import has_person


class DashboardWidgetObjectType(BaseObjectType):
    class Meta:
        model = DashboardWidget


class DashboardWidgetType(PermissionsTypeMixin, DjangoFilterMixin, graphene.Interface):
    class Meta:
        model = DashboardWidget

    id = graphene.ID()
    status = graphene.Field(graphene.Enum.from_enum(DashboardWidget.Status))
    title = graphene.String()


class DashboardWidgetInstanceType(BaseObjectType):
    class Meta:
        model = DashboardWidgetInstance
        fields = ["id", "x", "y", "width", "height"]

    context = graphene.JSONString()
    widget = graphene.Field(DashboardWidgetType)

    @staticmethod
    def resolve_context(root, info, **kwargs):
        return root.widget.get_context(info.context, root.configuration)


class AvailableDashboardWidgetType(ObjectType):
    model_name = graphene.String()
    type_name = graphene.String()

    @staticmethod
    def resolve_type_name(root, info, **kwargs):
        return get_global_registry().get_type_for_model(root)._meta.name

    @staticmethod
    def resolve_model_name(root, info, **kwargs):
        return root._class_name


class DashboardType(ObjectType):
    widgets = graphene.List(
        DashboardWidgetType,
        status=graphene.Argument(graphene.Enum.from_enum(DashboardWidget.Status)),
    )
    widget_types = graphene.List(AvailableDashboardWidgetType)

    my = graphene.List(
        DashboardWidgetInstanceType,
        force_default=graphene.Argument(graphene.Boolean),
    )
    has_own = graphene.Boolean()

    @staticmethod
    def resolve_widgets(root, info, status=None, **kwargs) -> QuerySet[DashboardWidget]:
        if info.context.user.has_perm("core.view_dashboardwidgets_rule"):
            if status is not None:
                return DashboardWidget.objects.filter(status=status).order_by("-id")
            return DashboardWidget.objects.all().order_by("-id")
        return DashboardWidget.objects.none()

    @staticmethod
    def resolve_widget_types(root, info, **kwargs):
        return DashboardWidget.registered_objects_list

    @staticmethod
    def resolve_single_widgets(root, info, **kwargs):
        return True

    @staticmethod
    def resolve_my(root, info, force_default=False, **kwargs):
        if not force_default and has_person(info.context.user):
            qs = DashboardWidgetInstance.objects.for_person(info.context.user.person)
            if qs.exists():
                return qs.order_by("y", "x")
        return DashboardWidgetInstance.objects.default_dashboard().order_by("y", "x")

    @staticmethod
    def resolve_has_own(root, info, **kwargs):
        return (
            has_person(info.context.user)
            and DashboardWidgetInstance.objects.for_person(info.context.user.person).exists()
        )


class ReorderDashboardWidgetInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    widget = graphene.ID(required=True)
    x = graphene.Int(required=True)
    y = graphene.Int(required=True)
    width = graphene.Int(required=True)
    height = graphene.Int(required=True)


class ReorderDashboardWidgetsMutation(graphene.Mutation):
    class Arguments:
        widget_data = graphene.List(ReorderDashboardWidgetInput, required=True)

        is_default_dashboard = graphene.Boolean(required=False)

    created = graphene.List(DashboardWidgetInstanceType)
    updated = graphene.List(DashboardWidgetInstanceType)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        widget_data: list[ReorderDashboardWidgetInput],
        is_default_dashboard=False,
    ):
        if is_default_dashboard and not info.context.user.has_perm(
            "core.edit_default_dashboard_rule"
        ):
            raise PermissionDenied

        person = None if is_default_dashboard else info.context.user.person

        created = []
        updated = []

        for w_data in widget_data:
            if w_data.id:
                widget = DashboardWidgetInstance.objects.get(id=w_data.id)
                updated.append(widget)
            else:
                widget = DashboardWidgetInstance()
                widget.widget = DashboardWidget.objects.get(pk=w_data.widget)
                created.append(widget)

            widget.x = w_data.x
            widget.y = w_data.y
            widget.width = w_data.width
            widget.height = w_data.height
            widget.person = person

            widget.save()

        return ReorderDashboardWidgetsMutation(created=created, updated=updated)


class CreateDashboardWidgetsMutation(graphene.Mutation):
    class Arguments:
        widget_types = graphene.List(graphene.String, required=True)

    created = graphene.List(DashboardWidgetType)

    @classmethod
    def mutate(cls, root, info, widget_types: list[str], **kwargs):
        created = []
        for type_name in widget_types:
            widget_class = DashboardWidget.get_object_by_name(type_name)

            if not widget_class:
                raise ValueError(f"Invalid dashboard widget subclass {type_name}")

            widget = widget_class()
            widget.title = f"{widget_class._meta.verbose_name} {random.randint(1000, 9999)}"  # noqa: S311
            widget.save()

            created.append(widget)

        return CreateDashboardWidgetsMutation(created=created)


class DashboardWidgetInstanceDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = DashboardWidgetInstance
        permissions = ("core.delete_dashboard_widget_instance_rule",)


class DashboardWidgetUpdateMutation(BaseBatchPatchMutation):
    class Meta:
        model = DashboardWidget
        permissions = ("core.edit_dashboardwidget_rule",)
        fields = (
            "id",
            "status",
            "title",
        )
        return_field_name = "dashboardWidgets"

    @classmethod
    def after_mutate(cls, root, info, input, updated_objs, return_data):  # noqa: A002
        return_data["dashboardWidgets"] = [obj.dashboardwidget_ptr for obj in updated_objs]


class DashboardWidgetDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = DashboardWidget
        permissions = ("core.delete_dashboardwidget_rule",)
