import base64
import json
from datetime import date

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

import pytest
from graphene_django.utils.testing import graphql_query
from graphql import GraphQLError

from aleksis.core.data_checks import ColorAccessibilityDataCheck
from aleksis.core.models import DataCheckResult, Group, Holiday, OAuthApplication, Person

pytestmark = pytest.mark.django_db


def test_all_settigns_registered():
    """Tests for regressions of preferences not being registered.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/592
    """

    from dynamic_preferences.types import BasePreferenceType

    from aleksis.core import preferences
    from aleksis.core.preferences import person_preferences_registry, site_preferences_registry

    for obj in preferences.__dict__.values():
        if not isinstance(obj, BasePreferenceType):
            continue

        in_site_reg = site_preferences_registry.get(obj.section.name, {}).get(obj.name, None) is obj
        in_person_reg = (
            person_preferences_registry.get(obj.section.name, {}).get(obj.name, None) is obj
        )

        assert in_site_reg != in_person_reg


def test_reassign_user_to_person():
    """Tests that on re-assigning a user, groups are correctly synced.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/628
    """

    User = get_user_model()

    group1 = Group.objects.create(name="Group 1")
    group2 = Group.objects.create(name="Group 2")

    user1 = User.objects.create(username="user1")
    user2 = User.objects.create(username="user2")

    person1 = Person.objects.create(first_name="Person", last_name="1", user=user1)
    person2 = Person.objects.create(first_name="Person", last_name="2", user=user2)

    person1.member_of.set([group1])
    person2.member_of.set([group2])

    assert user1.groups.count() == 1
    assert user2.groups.count() == 1
    assert user1.groups.first().name == "Group 1"
    assert user2.groups.first().name == "Group 2"

    person1.user = None
    person1.save()
    assert user1.groups.count() == 0

    person2.user = user1
    person2.save()
    person1.user = user2
    person1.save()

    assert user1.groups.count() == 1
    assert user2.groups.count() == 1
    assert user1.groups.first().name == "Group 2"
    assert user2.groups.first().name == "Group 1"


@override_settings(ROOT_URLCONF="aleksis.core.tests.regression.view_oauth")
def test_no_access_oauth2_client_credentials_without_allowed_scopes(client):
    """Tests that ClientProtectedResourceMixin doesn't allow access if no allowed scopes are set.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/688
    """

    wrong_application = OAuthApplication(
        name="Test Application",
        allowed_scopes=[],
        authorization_grant_type=OAuthApplication.GRANT_CLIENT_CREDENTIALS,
        client_type=OAuthApplication.CLIENT_CONFIDENTIAL,
        redirect_uris=["http://localhost:8000/"],
    )
    wrong_application_secret = wrong_application.client_secret
    wrong_application.save()
    wrong_application_2 = OAuthApplication(
        name="Test Application",
        allowed_scopes=["read"],
        authorization_grant_type=OAuthApplication.GRANT_CLIENT_CREDENTIALS,
        client_type=OAuthApplication.CLIENT_CONFIDENTIAL,
        redirect_uris=["http://localhost:8000/"],
    )
    wrong_application_2_secret = wrong_application_2.client_secret
    wrong_application_2.save()
    correct_application = OAuthApplication(
        name="Test Application",
        allowed_scopes=["write"],
        authorization_grant_type=OAuthApplication.GRANT_CLIENT_CREDENTIALS,
        client_type=OAuthApplication.CLIENT_CONFIDENTIAL,
        redirect_uris=["http://localhost:8000/"],
    )
    correct_application_secret = correct_application.client_secret
    correct_application.save()

    url = reverse("client_protected_resource_mixin_test")
    auth_header = (
        "Basic "
        + base64.b64encode(
            f"{wrong_application.client_id}:{wrong_application_secret}".encode()
        ).decode()
    )
    r = client.get(url, HTTP_AUTHORIZATION=auth_header)
    assert r.status_code == 403

    auth_header = (
        "Basic "
        + base64.b64encode(
            f"{wrong_application_2.client_id}:{wrong_application_2_secret}".encode()
        ).decode()
    )
    r = client.get(url, HTTP_AUTHORIZATION=auth_header)
    assert r.status_code == 403

    auth_header = (
        "Basic "
        + base64.b64encode(
            f"{correct_application.client_id}:{correct_application_secret}".encode()
        ).decode()
    )
    r = client.get(url, HTTP_AUTHORIZATION=auth_header)
    assert r.status_code == 200


def test_nested_queries_max_depth(logged_in_client):
    """Tests that queries enforces a maximum depth limit.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/1195
    """

    with pytest.raises(GraphQLError) as excinfo:
        graphql_query(
            """
            query person{
                personByIdOrMe{
                    id
                    memberOf{
                        id
                        members{
                            id
                            memberOf{
                                id
                                members{
                                    id
                                    memberOf{
                                        id
                                        members{
                                            id
                                            memberOf{
                                                id
                                                members{
                                                    id
                                                    memberOf{
                                                        id
                                                        members{
                                                            id
                                                            memberOf{
                                                                id
                                                                members{
                                                                    id
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """,
            client=logged_in_client,
        )

    assert "exceeds maximum operation depth" in str(excinfo.value)

    response = graphql_query(
        """
        query person{
            personByIdOrMe{
                id
                memberOf{
                    id
                    members{
                        id
                        memberOf{
                            id
                            members{
                                id
                                memberOf{
                                    id
                                    members{
                                        id
                                        memberOf{
                                            id
                                            members{
                                                id
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """,
        client=logged_in_client,
    )

    content = json.loads(response.content)
    assert "errors" not in content


def test_all_day_events_end_date():
    """Tests that CalendarEvent's value method returns a non-inclusive end date for all day events.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/1199
    """
    holiday = Holiday.objects.create(
        date_start=date(2024, 2, 1), date_end=date(2024, 2, 1), holiday_name="Test Holiday"
    )

    assert holiday.value_start_datetime(holiday) == date(2024, 2, 1)
    assert holiday.value_end_datetime(holiday) == date(2024, 2, 2)


def test_data_checks_delete_old_results():
    """Test that data checks run correctly with deleting old results.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/1293
    """

    g = Group.objects.create(name="Foo", short_name="foo")
    ColorAccessibilityDataCheck.register_result(g)
    ColorAccessibilityDataCheck._current_results = []

    assert DataCheckResult.objects.count() == 1

    ColorAccessibilityDataCheck.run_check_data()

    assert DataCheckResult.objects.count() == 0
