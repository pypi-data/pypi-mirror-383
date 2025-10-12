import pytest

from aleksis.core.models import Person

pytestmark = pytest.mark.django_db


def test_managed_by():
    managed_person = Person.objects.create(
        first_name="Jane", last_name="Doe", managed_by_app_label="core"
    )
    unmanaged_person_1 = Person.objects.create(first_name="Jane 2", last_name="Doe 2")
    unmanaged_person_2 = Person.objects.create(first_name="Jane 2", last_name="Doe 2")

    assert list(Person.objects.managed_by_app("core")) == [managed_person]

    assert list(Person.objects.all()) == [managed_person, unmanaged_person_1, unmanaged_person_2]
    assert list(Person.objects.unmanaged()) == [unmanaged_person_1, unmanaged_person_2]
