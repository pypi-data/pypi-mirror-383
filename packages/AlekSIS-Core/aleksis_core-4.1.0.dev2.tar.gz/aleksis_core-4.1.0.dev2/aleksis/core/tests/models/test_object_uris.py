from uuid import uuid4

from django.conf import settings

import pytest

from aleksis.core.mixins import ExtensibleModel
from aleksis.core.models import Group, Person

pytestmark = pytest.mark.django_db


def test_get_object_uri():
    _uuid = uuid4()
    _person = Person.objects.create(first_name="Jane", last_name="Doe", uuid=_uuid)

    assert _person.get_object_uri() == f"{settings.BASE_URL}/o/core/person/{_uuid}"


def test_from_object_uri_generic():
    _uuid = uuid4()
    _person = Person.objects.create(first_name="Jane", last_name="Doe", uuid=_uuid)

    assert ExtensibleModel.from_object_uri(f"{settings.BASE_URL}/o/core/person/{_uuid}") == _person


def test_from_object_uri_concrete():
    _uuid = uuid4()
    _person = Person.objects.create(first_name="Jane", last_name="Doe", uuid=_uuid)

    assert Person.from_object_uri(f"{settings.BASE_URL}/o/core/person/{_uuid}") == _person


def test_from_object_uri_wrong_cls():
    _uuid = uuid4()
    _person = Person.objects.create(first_name="Jane", last_name="Doe", uuid=_uuid)

    assert Group.from_object_uri(f"{settings.BASE_URL}/o/core/person/{_uuid}") is None


def test_from_object_uri_no_match():
    assert Person.from_object_uri("foo") is None
