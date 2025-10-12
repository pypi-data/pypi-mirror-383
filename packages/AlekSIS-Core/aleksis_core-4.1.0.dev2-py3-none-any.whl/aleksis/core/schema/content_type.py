from django.contrib.contenttypes.models import ContentType

import graphene
from graphene_django import DjangoObjectType


class ContentTypeType(DjangoObjectType):
    class Meta:
        model = ContentType
        fields = (
            "id",
            "app_label",
            "model",
            "verbose_name",
        )

    verbose_name = graphene.String(required=True)

    @staticmethod
    def resolve_verbose_name(root, info, **kwargs):
        return root.app_labeled_name
