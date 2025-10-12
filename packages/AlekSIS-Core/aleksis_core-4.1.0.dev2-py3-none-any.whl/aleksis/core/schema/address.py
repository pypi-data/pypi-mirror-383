from graphene_django import DjangoObjectType

from ..models import Address, AddressType
from .base import (
    DjangoFilterMixin,
    PermissionsTypeMixin,
)


class AddressTypeType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = AddressType
        fields = ["id", "name"]


class AddressType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = Address
        fields = ["id", "address_types", "street", "housenumber", "postal_code", "place", "country"]
