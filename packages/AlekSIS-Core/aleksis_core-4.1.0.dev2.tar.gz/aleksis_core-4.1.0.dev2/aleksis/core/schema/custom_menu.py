import graphene
from graphene_django import DjangoObjectType

from ..models import CustomMenu, CustomMenuItem


class CustomMenuItemType(DjangoObjectType):
    class Meta:
        model = CustomMenuItem
        convert_choices_to_enum = False

    name = graphene.Field(graphene.String)
    url = graphene.Field(graphene.String)
    icon = graphene.Field(graphene.String)


class CustomMenuType(DjangoObjectType):
    class Meta:
        model = CustomMenu

    name = graphene.Field(graphene.String)
    items = graphene.List(CustomMenuItemType)

    def resolve_items(root, info, **kwargs):
        return root.items.all()
