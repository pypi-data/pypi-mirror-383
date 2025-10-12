import graphene
from graphene_django import DjangoObjectType

from ..models import SchoolTerm
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    DjangoFilterMixin,
    PermissionsTypeMixin,
)


class SchoolTermType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = SchoolTerm
        filter_fields = {
            "name": ["icontains", "exact"],
            "date_start": ["exact", "lt", "lte", "gt", "gte"],
            "date_end": ["exact", "lt", "lte", "gt", "gte"],
        }
        fields = ("id", "name", "date_start", "date_end")

    current = graphene.Boolean()

    @staticmethod
    def resolve_current(root, info):
        return (current := SchoolTerm.current) and root.pk == current.pk


class SchoolTermBatchCreateMutation(BaseBatchCreateMutation):
    class Meta:
        model = SchoolTerm
        permissions = ("core.create_schoolterm_rule",)
        only_fields = ("id", "name", "date_start", "date_end")


class SchoolTermBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = SchoolTerm
        permissions = ("core.delete_schoolterm_rule",)


class SchoolTermBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = SchoolTerm
        permissions = ("core.edit_schoolterm_rule",)
        only_fields = ("id", "name", "date_start", "date_end")


class SetActiveSchoolTermMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)  # noqa

    active_school_term = graphene.Field(SchoolTermType)

    @classmethod
    def mutate(cls, root, info, id):  # noqa
        school_term = SchoolTerm.objects.get(id=id)
        info.context.session["active_school_term"] = school_term.pk

        return SetActiveSchoolTermMutation(active_school_term=school_term)
