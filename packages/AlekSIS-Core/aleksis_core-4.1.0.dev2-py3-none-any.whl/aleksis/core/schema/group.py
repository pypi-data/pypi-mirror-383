import graphene
from graphene_django import DjangoObjectType
from guardian.shortcuts import get_objects_for_user

from ..models import Group, Person, PersonGroupThrough
from ..util.core_helpers import has_person
from .base import BaseBatchDeleteMutation, BaseObjectType, DjangoFilterMixin, PermissionsTypeMixin


class GroupStatisticsType(graphene.ObjectType):
    members = graphene.Int()
    age_avg = graphene.Float()
    age_range_min = graphene.Int()
    age_range_max = graphene.Int()


class PersonGroupThroughType(BaseObjectType):
    """GraphQL type for PersonGroupThrough"""

    class Meta:
        model = PersonGroupThrough
        fields = [
            "group",
            "person",
            "roles",
        ]


class GroupType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = Group
        fields = [
            "id",
            "school_term",
            "name",
            "short_name",
            "members",
            "owners",
            "child_groups",
            "parent_groups",
            "group_type",
            "photo",
            "avatar",
        ]
        filter_fields = {
            "name": ["icontains"],
            "short_name": ["icontains"],
            "group_type": ["exact", "in"],
        }

    avatar_url = graphene.String()
    statistics = graphene.Field(GroupStatisticsType)

    relationships = graphene.List(PersonGroupThroughType)

    @staticmethod
    def resolve_parent_groups(root, info, **kwargs):
        qs = root.parent_groups.all()
        if info.context.user.has_perm("core.view_group_rule", root):
            return qs
        return get_objects_for_user(info.context.user, "core.view_group", qs)

    @staticmethod
    def resolve_child_groups(root, info, **kwargs):
        qs = root.child_groups.all()
        if info.context.user.has_perm("core.view_group_rule", root):
            return qs
        return get_objects_for_user(info.context.user, "core.view_group", qs)

    @staticmethod
    def resolve_members(root, info, **kwargs):
        if (
            has_person(info.context.user)
            and root.group_type
            and root.group_type.owners_can_see_members
            and info.context.user.person in root.owners.all()
        ):
            return root.members.all()
        persons = get_objects_for_user(info.context.user, "core.view_person", root.members.all())
        if has_person(info.context.user) and [
            m for m in root.members.all() if m.pk == info.context.user.person.pk
        ]:
            persons = (persons | Person.objects.filter(pk=info.context.user.person.pk)).distinct()
        return persons

    @staticmethod
    def resolve_relationships(root: Group, info, **kwargs):
        persons = GroupType.resolve_members(root, info, **kwargs)
        return PersonGroupThrough.objects.filter(group=root, person__in=persons)

    @staticmethod
    def resolve_owners(root, info, **kwargs):
        persons = get_objects_for_user(info.context.user, "core.view_person", root.owners.all())
        if has_person(info.context.user) and [
            o for o in root.owners.all() if o.pk == info.context.user.person.pk
        ]:
            persons = (persons | Person.objects.filter(pk=info.context.user.person.pk)).distinct()
        return persons

    @staticmethod
    def resolve_statistics(root: Group, info, **kwargs):
        if not info.context.user.has_perm("core.view_group_stats_rule", root):
            return None
        return root.get_group_stats

    @staticmethod
    def resolve_can_edit(root, info, **kwargs):
        if hasattr(root, "can_edit"):
            return root.can_edit
        return info.context.user.has_perm("core.edit_group_rule", root)

    @staticmethod
    def resolve_can_delete(root, info, **kwargs):
        if hasattr(root, "can_delete"):
            return root.can_delete
        return info.context.user.has_perm("core.delete_group_rule", root)


class GroupBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = Group
        permissions = ("core.delete_group_rule",)
