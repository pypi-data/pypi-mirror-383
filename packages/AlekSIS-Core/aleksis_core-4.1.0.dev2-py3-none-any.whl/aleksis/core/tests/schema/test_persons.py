from django.contrib.auth.models import Permission

import pytest

from aleksis.core.models import Group, GroupType, Person

pytestmark = pytest.mark.django_db


def test_persons_query(client_query):
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

    correct_member = Person.objects.create(first_name="correct_member", last_name="correct_member")
    correct_member_2 = Person.objects.create(
        first_name="correct_member_2", last_name="correct_member_2"
    )
    wrong_member = Person.objects.create(first_name="wrong_member", last_name="wrong_member")

    for g in (group_correct_group_type_owner, group2_correct_group_type_owner):
        g.members.add(correct_member, correct_member_2)

    for g in (group_not_owner, group_wrong_group_type_owner, group_no_group_type_owner):
        g.members.add(wrong_member)

    response, content = client_query("{persons{id}}")
    assert len(content["data"]["persons"]) == 1
    assert content["data"]["persons"][0]["id"] == str(p.id)

    for g in Person.objects.exclude(pk=p.id):
        response, content = client_query(
            "query personById($id: ID) {object: personById(id: $id) { id } }",
            variables={"id": g.id},
        )
        assert content["data"]["object"] is None

    global_permission = Permission.objects.get(
        codename="view_person", content_type__app_label="core"
    )
    p.user.user_permissions.add(global_permission)

    response, content = client_query("{persons{id}}")
    assert set(int(g["id"]) for g in content["data"]["persons"]) == set(
        Person.objects.values_list("id", flat=True)
    )

    p.user.user_permissions.remove(global_permission)

    correct_group_type.owners_can_see_members = True
    correct_group_type.save()

    response, content = client_query("{persons{id}}")
    assert set(int(g["id"]) for g in content["data"]["persons"]) == {
        p.id,
        correct_member.id,
        correct_member_2.id,
    }

    for g in (correct_member, correct_member_2):
        response, content = client_query(
            "query personById($id: ID) {object: personById(id: $id) { id } }",
            variables={"id": g.id},
        )
        assert content["data"]["object"]["id"] == str(g.id)

    response, content = client_query(
        "query personById($id: ID) {object: personById(id: $id) { id } }",
        variables={"id": wrong_member.id},
    )
    assert content["data"]["object"] is None


def test_create_person_with_file_upload(client_query, uploaded_picture):
    p = Person.objects.first()
    global_permission = Permission.objects.get(
        codename="add_person", content_type__app_label="core"
    )
    p.user.user_permissions.add(global_permission)

    query = """
    mutation createPersons($input: [BatchCreatePersonInput]!) {
      createPersons(input: $input) {
        items: persons {
          id
          firstName
          lastName
        }
      }
    }
    """
    variables = {
        "input": [
            {
                "firstName": "Foo",
                "lastName": "Bar",
                "photo": None,
                "avatar": None,
            },
        ]
    }
    files = {
        "variables.input.0.photo": uploaded_picture,
        "variables.input.0.avatar": uploaded_picture,
    }

    response, content = client_query(query, variables=variables, files=files)
    person_id = content["data"]["createPersons"]["items"][0]["id"]

    created_person = Person.objects.get(id=person_id)
    assert created_person.first_name == "Foo"
    assert created_person.last_name == "Bar"
    assert created_person.photo.file.name.endswith(".jpg")
    assert created_person.avatar.file.name.endswith(".jpg")


def test_edit_person_with_file_upload(client_query, uploaded_picture):
    p = Person.objects.first()
    global_permission = Permission.objects.get(
        codename="change_person", content_type__app_label="core"
    )
    p.user.user_permissions.add(global_permission)

    p = Person.objects.create(
        first_name="Foo",
        last_name="Bar",
    )

    query = """
    mutation updatePersons($input: [BatchPatchPersonInput]!) {
      updatePersons(input: $input) {
        items: persons {
          id
          firstName
          lastName
        }
      }
    }
    """

    # Edit with adding files
    variables = {
        "input": [
            {
                "id": p.id,
                "firstName": "Foo",
                "lastName": "Bar",
                "photo": None,
                "avatar": None,
            },
        ]
    }
    files = {
        "variables.input.0.photo": uploaded_picture,
        "variables.input.0.avatar": uploaded_picture,
    }

    response, content = client_query(query, variables=variables, files=files)

    p.refresh_from_db()

    assert p.first_name == "Foo"
    assert p.last_name == "Bar"
    assert p.photo.file.name.endswith(".jpg")
    assert p.avatar.file.name.endswith(".jpg")

    # Edit without changing files
    variables = {
        "input": [
            {
                "id": p.id,
                "firstName": "Foo",
                "lastName": "Baz",
            },
        ]
    }
    files = {}
    response, content = client_query(query, variables=variables, files=files)
    p.refresh_from_db()

    assert p.first_name == "Foo"
    assert p.last_name == "Baz"
    assert p.photo.file.name.endswith(".jpg")
    assert p.avatar.file.name.endswith(".jpg")

    # Edit with deleting files
    variables = {
        "input": [
            {
                "id": p.id,
                "firstName": "Foo",
                "lastName": "Baz",
                "photo": None,
                "avatar": None,
            },
        ]
    }
    response, content = client_query(query, variables=variables, files=files)
    p.refresh_from_db()

    assert p.first_name == "Foo"
    assert p.last_name == "Baz"
    assert not p.photo
    assert not p.avatar


def test_create_person_with_address(client_query):
    p = Person.objects.first()
    global_permission = Permission.objects.get(
        codename="add_person", content_type__app_label="core"
    )
    p.user.user_permissions.add(global_permission)

    query = """
    mutation createPersons($input: [BatchCreatePersonInput]!) {
      createPersons(input: $input) {
        items: persons {
          id
          firstName
          lastName
        }
      }
    }
    """
    variables = {
        "input": [
            {
                "firstName": "Foo",
                "lastName": "Bar",
                "street": "Teststreet",
                "housenumber": "123",
                "postalCode": "12345",
                "place": "Testcity",
                "country": "DE",
            },
        ]
    }

    response, content = client_query(query, variables=variables)
    person_id = content["data"]["createPersons"]["items"][0]["id"]

    created_person = Person.objects.get(id=person_id)
    assert created_person.addresses.count() == 1

    address = created_person.addresses.first()
    assert address.street == "Teststreet"
    assert address.housenumber == "123"
    assert address.postal_code == "12345"
    assert address.place == "Testcity"
    assert address.country == "DE"


def test_edit_person_with_address(client_query, uploaded_picture):
    p = Person.objects.first()
    global_permission = Permission.objects.get(
        codename="change_person", content_type__app_label="core"
    )
    p.user.user_permissions.add(global_permission)

    p = Person.objects.create(
        first_name="Foo",
        last_name="Bar",
    )

    query = """
    mutation updatePersons($input: [BatchPatchPersonInput]!) {
      updatePersons(input: $input) {
        items: persons {
          id
          firstName
          lastName
        }
      }
    }
    """

    # Edit with adding address
    variables = {
        "input": [
            {
                "id": p.id,
                "firstName": "Foo",
                "lastName": "Bar",
                "street": "Teststreet",
                "housenumber": "123",
                "postalCode": "12345",
                "place": "Testcity",
                "country": "DE",
            },
        ]
    }
    response, content = client_query(query, variables=variables)

    p.refresh_from_db()

    assert p.addresses.count() == 1
    address = p.addresses.first()
    assert address.street == "Teststreet"
    assert address.housenumber == "123"
    assert address.postal_code == "12345"
    assert address.place == "Testcity"
    assert address.country == "DE"

    # Edit without changing address
    variables = {
        "input": [
            {
                "id": p.id,
                "firstName": "Foo",
                "lastName": "Baz",
            },
        ]
    }
    response, content = client_query(query, variables=variables)
    p.refresh_from_db()

    assert p.addresses.count() == 1
    address = p.addresses.first()
    assert address.street == "Teststreet"
    assert address.housenumber == "123"
    assert address.postal_code == "12345"
    assert address.place == "Testcity"
    assert address.country == "DE"
    # assert address.address_types.count() == 1
    # assert address.address_types.first().name == "default"

    # Edit with changing address
    variables = {
        "input": [
            {
                "id": p.id,
                "firstName": "Foo",
                "lastName": "Bar",
                "street": "Teststreetnew",
                "housenumber": "123new",
                "postalCode": "12345new",
                "place": "Testcitynew",
                "country": "GB",
            },
        ]
    }
    response, content = client_query(query, variables=variables)

    p.refresh_from_db()

    assert p.addresses.count() == 1
    address = p.addresses.first()
    assert address.street == "Teststreetnew"
    assert address.housenumber == "123new"
    assert address.postal_code == "12345new"
    assert address.place == "Testcitynew"
    assert address.country == "GB"

    # Edit with deleting address
    variables = {
        "input": [
            {
                "id": p.id,
                "firstName": "Foo",
                "lastName": "Baz",
                "street": None,
                "housenumber": None,
                "postalCode": None,
                "place": None,
                "country": None,
            },
        ]
    }
    response, content = client_query(query, variables=variables)
    p = Person.objects.get(id=p.id)

    assert p.addresses.count() == 0
