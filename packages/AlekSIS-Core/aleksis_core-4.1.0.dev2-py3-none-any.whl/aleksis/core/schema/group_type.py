import graphene_django_optimizer
from graphene_django import DjangoObjectType

from ..models import GroupType
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    DjangoFilterMixin,
    PermissionsTypeMixin,
)


class GroupTypeType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = GroupType
        fields = [
            "id",
            "name",
            "description",
            "owners_can_see_groups",
            "owners_can_see_members",
            "owners_can_see_members_allowed_information",
            "available_roles",
        ]

    @staticmethod
    def resolve_available_roles(root, info, **kwargs):
        return graphene_django_optimizer.query(root.available_roles.all(), info)


class GroupTypeBatchCreateMutation(BaseBatchCreateMutation):
    class Meta:
        model = GroupType
        permissions = ("core.create_grouptype_rule",)
        only_fields = (
            "name",
            "description",
            "owners_can_see_groups",
            "owners_can_see_members",
            "owners_can_see_members_allowed_information",
            "available_roles",
        )


class GroupTypeBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = GroupType
        permissions = ("core.delete_grouptype_rule",)


class GroupTypeBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = GroupType
        permissions = ("core.edit_grouptype_rule",)
        only_fields = (
            "id",
            "name",
            "description",
            "owners_can_see_groups",
            "owners_can_see_members",
            "owners_can_see_members_allowed_information",
            "available_roles",
        )
