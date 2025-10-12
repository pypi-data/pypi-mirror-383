import graphene
from graphene_django import DjangoObjectType

from ..models import PersonInvitation


class PersonInvitationType(DjangoObjectType):
    class Meta:
        model = PersonInvitation
        fields = [
            "id",
        ]

    valid = graphene.Boolean()
    has_email = graphene.Boolean()
    has_person = graphene.Boolean()

    @staticmethod
    def resolve_valid(root, info, **kwargs):
        return not root.accepted and not root.key_expired()

    @staticmethod
    def resolve_has_email(root, info, **kwargs):
        return bool(root.email)

    @staticmethod
    def resolve_has_person(root, info, **kwargs):
        return bool(root.person)
