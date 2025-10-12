from django.test import override_settings
from django.urls import reverse

from aleksis.core.models import UserAdditionalAttributes

try:
    import ldap

    HAS_LDAP = True
    from django_auth_ldap.config import LDAPSearch

    LDAP_BASE = "dc=example,dc=com"
    LDAP_SETTINGS = {
        "AUTH_LDAP_GLOBAL_OPTIONS": {
            ldap.OPT_NETWORK_TIMEOUT: 1,
        },
        "AUTH_LDAP_USER_SEARCH": LDAPSearch(LDAP_BASE, ldap.SCOPE_SUBTREE),
    }
except ImportError:
    HAS_LDAP = False
    LDAP_SETTINGS = {}
import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.skip(reason="broken")
@override_settings(
    AUTHENTICATION_BACKENDS=[
        "aleksis.core.util.ldap.LDAPBackend",
        "django.contrib.auth.backends.ModelBackend",
    ],
    AUTH_LDAP_SERVER_URI="ldap://[100::0]",
    AUTH_LDAP_SET_USABLE_PASSWORD=True,
    **LDAP_SETTINGS,
)
def test_login_ldap_fail_if_previously_ldap_authenticated(client, django_user_model):
    username = "foo"
    password = "bar"

    django_user_model.objects.create_user(username=username, password=password)

    # Logging in with a fresh account should success
    res = client.login(username=username, password=password)
    assert res
    client.get(reverse("logout"), follow=True)

    # Logging in with a previously LDAP-authenticated account should fail
    UserAdditionalAttributes.set_user_attribute(username, "ldap_authenticated", True)
    res = client.login(username=username, password=password)
    assert not res

    # Explicitly noting account has not been used with LDAP should succeed
    UserAdditionalAttributes.set_user_attribute(username, "ldap_authenticated", False)
    res = client.login(username=username, password=password)
    assert res


if not HAS_LDAP:
    test_login_ldap_fail_if_previously_ldap_authenticated = pytest.mark.skip(
        reason="ldap module not available"
    )(test_login_ldap_fail_if_previously_ldap_authenticated)
