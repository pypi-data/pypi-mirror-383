from django.contrib.auth.models import Permission

import pytest

from aleksis.core.models import Group, GroupType, Person

pytestmark = pytest.mark.django_db


def test_groups_query(client_query):
    p = Person.objects.first()
    correct_group_type = GroupType.objects.create(name="correct")
    wrong_group_type = GroupType.objects.create(name="wrong")

    group_not_owner = Group.objects.create(name="not_owner")
    group_correct_group_type_owner = Group.objects.create(
        name="correct_group_type_owner", group_type=correct_group_type
    )

    group2_correct_group_type_owner = Group.objects.create(
        name="correct_group_type_owner", group_type=correct_group_type
    )
    group_wrong_group_type_owner = Group.objects.create(
        name="wrong_group_type_owner", group_type=wrong_group_type
    )
    group_no_group_type_owner = Group.objects.create(name="no_group_type_owner")

    for g in (
        group_correct_group_type_owner,
        group2_correct_group_type_owner,
        group_wrong_group_type_owner,
        group_no_group_type_owner,
    ):
        g.owners.add(p)

    response, content = client_query("{groups{id}}")
    assert len(content["data"]["groups"]) == 0

    for g in Group.objects.all():
        response, content = client_query(
            "query groupById($id: ID) {object: groupById(id: $id) { id } }",
            variables={"id": g.id},
        )
        assert content["data"]["object"] is None

    global_permission = Permission.objects.get(
        codename="view_group", content_type__app_label="core"
    )
    p.user.user_permissions.add(global_permission)

    response, content = client_query("{groups{id}}")
    assert set(int(g["id"]) for g in content["data"]["groups"]) == set(
        Group.objects.values_list("id", flat=True)
    )

    p.user.user_permissions.remove(global_permission)

    correct_group_type.owners_can_see_groups = True
    correct_group_type.save()

    response, content = client_query("{groups{id}}")
    assert set(int(g["id"]) for g in content["data"]["groups"]) == {
        group_correct_group_type_owner.id,
        group2_correct_group_type_owner.id,
    }

    for g in (group_correct_group_type_owner, group2_correct_group_type_owner):
        response, content = client_query(
            "query groupById($id: ID) {object: groupById(id: $id) { id } }",
            variables={"id": g.id},
        )
        assert content["data"]["object"]["id"] == str(g.id)

    for g in (group_not_owner, group_wrong_group_type_owner, group_no_group_type_owner):
        response, content = client_query(
            "query groupById($id: ID) {object: groupById(id: $id) { id } }",
            variables={"id": g.id},
        )
        assert content["data"]["object"] is None
