import json
from collections.abc import Iterable

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import BadRequest, PermissionDenied
from django.db.models import Model
from django.utils import timezone

import graphene
import reversion
from django_filters.filterset import FilterSet, filterset_factory
from graphene_django import DjangoListField, DjangoObjectType
from graphene_django_cud.mutations.batch_create import DjangoBatchCreateMutation
from graphene_django_cud.mutations.batch_delete import DjangoBatchDeleteMutation
from graphene_django_cud.mutations.batch_patch import DjangoBatchPatchMutation
from reversion import set_comment, set_user

from ..util.core_helpers import queryset_rules_filter


class RulesObjectType(DjangoObjectType):
    class Meta:
        abstract = True

    @classmethod
    def get_queryset(cls, queryset, info, perm):
        q = super().get_queryset(queryset, info)

        return queryset_rules_filter(info.context, q, perm)


class FieldFileType(graphene.ObjectType):
    url = graphene.String()
    absolute_url = graphene.String()
    name = graphene.String()

    def resolve_url(root, info, **kwargs):
        return root.url if root else ""

    def resolve_absolute_url(root, info, **kwargs):
        return info.context.build_absolute_uri(root.url) if root else ""

    def resolve_name(root, info, **kwargs):
        return root.name if root else ""


class Color(graphene.String):
    pass


class Weekday(graphene.Int):
    pass


class DeleteMutation(graphene.Mutation):
    """Mutation to delete an object."""

    klass: Model = None
    permission_required: str = ""
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID()  # noqa

    @classmethod
    def mutate(cls, root, info, **kwargs):
        obj = cls.klass.objects.get(pk=kwargs["id"])
        if info.context.user.has_perm(cls.permission_required, obj):
            obj.delete()
            return cls(ok=True)
        else:
            raise PermissionDenied()


class PermissionsTypeMixin:
    """Mixin for adding permissions to a Graphene type.

    To configure the names for the permissions or to do
    different permission checking, override the respective
    methods `resolve_can_edit` and `resolve_can_delete`
    """

    can_edit = graphene.Boolean()
    can_delete = graphene.Boolean()

    @staticmethod
    def resolve_can_edit(root: Model, info, **kwargs):
        if hasattr(root, "managed_by_app_label") and root.managed_by_app_label != "":
            return False
        content_type = ContentType.objects.get_for_model(root)
        perm = f"{content_type.app_label}.edit_{content_type.model}_rule"
        return info.context.user.has_perm(perm, root)

    @staticmethod
    def resolve_can_delete(root: Model, info, **kwargs):
        if hasattr(root, "managed_by_app_label") and root.managed_by_app_label != "":
            return False
        content_type = ContentType.objects.get_for_model(root)
        perm = f"{content_type.app_label}.delete_{content_type.model}_rule"
        return info.context.user.has_perm(perm, root)


class OptimisticResponseTypeMixin:
    """Mixin for using OptimisticResponse in the frontend.

    In the frontend, Apollo can be configured to show an optimistic
    response defined by the developer although the actual request
    isn't yet finished. This way the frontend can directly update
    and replace the optimistc data with the actual data from the
    backend when the request is finished.

    To know whether a response is optimistic or real, the field
    `is_optimistic` can be set to true in the frontend.
    """

    is_optimistic = graphene.Boolean(default_value=False)


class PermissionBatchCreateMixin:
    """Mixin for permission checking during batch create mutations."""

    class Meta:
        login_required = True

    @classmethod
    def check_permissions(cls, root, info, input, *args, **kwargs):  # noqa: A002
        pass

    @classmethod
    def after_create_obj(cls, root, info, data, obj, input):  # noqa
        super().after_create_obj(root, info, data, obj, input)
        if not isinstance(cls._meta.permissions, Iterable) or not info.context.user.has_perms(
            cls._meta.permissions, obj
        ):
            raise PermissionDenied()


class PermissionBatchPatchMixin:
    """Mixin for permission checking during batch patch mutations."""

    class Meta:
        login_required = True

    @classmethod
    def check_permissions(cls, root, info, input, *args, **kwargs):  # noqa: A002
        pass

    @classmethod
    def after_update_obj(cls, root, info, input, obj, full_input):  # noqa
        super().after_update_obj(root, info, input, obj, full_input)
        if (
            hasattr(obj, "managed_by_app_label")
            and obj.managed_by_app_label != ""
            or not isinstance(cls._meta.permissions, Iterable)
            or not info.context.user.has_perms(cls._meta.permissions, obj)
        ):
            raise PermissionDenied()


class PermissionBatchDeleteMixin:
    """Mixin for permission checking during batch delete mutations."""

    class Meta:
        login_required = True

    @classmethod
    def check_permissions(cls, root, info, input, *args, **kwargs):  # noqa: A002
        pass

    @classmethod
    def before_save(cls, root, info, ids, qs_to_delete):  # noqa
        super().before_save(root, info, ids, qs_to_delete)
        if not isinstance(cls._meta.permissions, Iterable):
            raise PermissionDenied()
        for obj in qs_to_delete:
            if (
                hasattr(obj, "managed_by_app_label")
                and obj.managed_by_app_label != ""
                or not info.context.user.has_perms(cls._meta.permissions, obj)
            ):
                raise PermissionDenied()


class PermissionPatchMixin:
    """Mixin for permission checking during patch mutations."""

    class Meta:
        login_required = True

    @classmethod
    def check_permissions(cls, root, info, input, id, obj):  # noqa
        if info.context.user.has_perms(cls._meta.permissions, root):
            return

        raise PermissionDenied()


class DjangoFilterMixin:
    """Filters a queryset with django filter."""

    @classmethod
    def get_filterset(cls):
        meta = getattr(cls, "_meta", None)

        if not meta:
            raise NotImplementedError(f"{cls.__name__} must implement class Meta for filtering.")

        if hasattr(meta, "filterset_class"):
            filterset = meta.filterset_class
            if filterset is not None:
                return filterset

        model: Model = meta.model
        fields = getattr(meta, "filter_fields", None)

        if not model:
            raise NotImplementedError(f"{cls.__name__} must supply a model via the Meta class")

        if not fields:
            # Django filter doesn't allow to filter without explicit fields
            raise NotImplementedError(
                f"{cls.__name__}.Meta must contain filter_fields or a filterset_class"
            )

        fs = filterset_factory(model=model, fields=fields)

        return fs

    @classmethod
    def filter(cls, filters, queryset):  # noqa
        filterset_class = cls.get_filterset()
        filterset: FilterSet = filterset_class(filters, queryset)
        return filterset.qs


class FilterOrderList(DjangoListField):
    """Generic filterable Field for lists of django models."""

    def __init__(self, _type, *args, **kwargs):
        kwargs.update(order_by=graphene.List(graphene.String))
        kwargs.update(filters=graphene.JSONString())
        super().__init__(_type, *args, **kwargs)

    @staticmethod
    def list_resolver(
        django_object_type,
        resolver,
        default_manager,
        root,
        info,
        order_by=None,
        filters=None,
        **args,
    ):
        qs = DjangoListField.list_resolver(
            django_object_type, resolver, default_manager, root, info, **args
        )

        if filters is not None:
            if isinstance(filters, str):
                filters = json.loads(filters)

            if isinstance(filters, dict) and len(filters.keys()) > 0:
                for f_key, f_value in filters.items():
                    if isinstance(f_value, list):
                        filters[f_key] = ",".join(map(str, f_value))

                qs = django_object_type.filter(filters, qs)

        if order_by is not None:
            if isinstance(order_by, str):
                order_by = [order_by]

            qs = qs.order_by(*order_by)

        return qs


class MutateWithRevisionMixin:
    """Mixin for creating revision for mutation."""

    @classmethod
    def mutate(cls, root, info, *args, **kwargs):
        with reversion.create_revision():
            set_user(info.context.user)
            set_comment(cls.__name__)
            return super().mutate(root, info, *args, **kwargs)


class ModelValidationMixin:
    """Mixin for executing model validation mechanisms."""

    @classmethod
    def after_update_obj(cls, root, info, data, obj, full_input):
        super().after_update_obj(root, info, data, obj, full_input)
        obj.full_clean()

    @classmethod
    def before_create_obj(cls, info, data, obj):
        super().before_create_obj(info, data, obj)
        obj.full_clean()


class BaseObjectType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        abstract = True


class BaseBatchCreateMutation(
    ModelValidationMixin,
    MutateWithRevisionMixin,
    PermissionBatchCreateMixin,
    DjangoBatchCreateMutation,
):
    class Meta:
        abstract = True


class BaseBatchPatchMutation(
    ModelValidationMixin,
    MutateWithRevisionMixin,
    PermissionBatchPatchMixin,
    DjangoBatchPatchMutation,
):
    class Meta:
        abstract = True


class BaseBatchDeleteMutation(
    MutateWithRevisionMixin, PermissionBatchDeleteMixin, DjangoBatchDeleteMutation
):
    class Meta:
        abstract = True


class CalendarEventBatchCreateMixin:
    """Mixin handling the timezone in the BatchCreateMutation of CalendarEvents."""

    @classmethod
    def handle_datetime_start(cls, value, name, info):
        value = value.replace(tzinfo=timezone.get_default_timezone())
        return value

    @classmethod
    def handle_datetime_end(cls, value, name, info):
        value = value.replace(tzinfo=timezone.get_default_timezone())
        return value


class CalendarEventBatchPatchMixin:
    """Mixin handling mutating of CalendarEvents.
    Handles switching between date & datetime.
    Handles removing recurrences.
    """

    @classmethod
    def before_mutate(cls, root, info, input):  # noqa
        super().before_mutate(root, info, input)
        for event in input:
            # Assure either date or datetime is set to None
            if "datetime_start" in event and "datetime_end" in event:
                event["date_start"] = None
                event["date_end"] = None
            elif "date_start" in event and "date_end" in event:
                event["datetime_start"] = None
                event["datetime_end"] = None
            else:
                raise BadRequest(
                    "Set either date_start and date_end or datetime_start and datetime_end"
                )

            # Remove recurrences if none were received.
            if "recurrences" not in event:
                event["recurrences"] = ""

        return input
