from graphene_django import DjangoObjectType

from ..models import Role
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    DjangoFilterMixin,
    PermissionsTypeMixin,
)


class RoleType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    """GraphQL type for Role"""

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "short_name",
            "reciprocal_name",
            "ical_participation_role",
            "vcard_related_type",
            "fg_color",
            "bg_color",
        ]


class RoleBatchCreateMutation(BaseBatchCreateMutation):
    """GraphQL batch create mutation for Role"""

    class Meta:
        model = Role
        permissions = ("core.create_role_rule",)
        only_fields = (
            "name",
            "short_name",
            "reciprocal_name",
            "ical_participation_role",
            "vcard_related_type",
            "fg_color",
            "bg_color",
        )
        optional_fields = (
            "ical_participation_role",
            "vcard_related_type",
            "fg_color",
            "bg_color",
        )


class RoleBatchDeleteMutation(BaseBatchDeleteMutation):
    """GraphQL batch delete mutation for Role"""

    class Meta:
        model = Role
        permissions = ("core.delete_role_rule",)


class RoleBatchPatchMutation(BaseBatchPatchMutation):
    """GraphQL batch patch mutation for Role"""

    class Meta:
        model = Role
        permissions = ("core.edit_role_rule",)
        only_fields = (
            "id",
            "name",
            "short_name",
            "reciprocal_name",
            "ical_participation_role",
            "vcard_related_type",
            "fg_color",
            "bg_color",
        )
