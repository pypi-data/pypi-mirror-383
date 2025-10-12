from graphene_django import DjangoObjectType

from ..models import Room
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    DjangoFilterMixin,
    PermissionsTypeMixin,
)


class RoomType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = Room
        fields = ("id", "name", "short_name")
        filter_fields = {
            "id": ["exact", "lte", "gte"],
            "name": ["icontains"],
            "short_name": ["icontains"],
        }


class RoomBatchCreateMutation(BaseBatchCreateMutation):
    class Meta:
        model = Room
        permissions = ("core.create_room_rule",)
        only_fields = ("id", "name", "short_name")


class RoomBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = Room
        permissions = ("core.delete_room_rule",)


class RoomBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = Room
        permissions = ("core.edit_room_rule",)
        only_fields = ("id", "name", "short_name")
