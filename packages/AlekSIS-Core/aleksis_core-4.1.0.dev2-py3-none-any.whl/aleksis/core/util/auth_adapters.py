import logging
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import get_login_redirect_url
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from invitations.adapters import BaseInvitationsAdapter

from ..templatetags.html_helpers import remove_prefix


class OurSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Customised adapter that recognises other authentication mechanisms."""

    def pre_social_login(self, request, sociallogin):
        # Try to match social accounts to local accounts by their username if enabled
        if (
            settings.ALEKSIS_SOCIALACCOUNT_USERNAME_MATCHING
            and not sociallogin.is_existing
            and sociallogin.account.extra_data.get("preferred_username")
        ):
            username = sociallogin.account.extra_data["preferred_username"]
            try:
                user = get_user_model().objects.get(username=username)
                sociallogin.user = user
                logging.info(f"Match local account {username} to social account")
            except get_user_model().DoesNotExist:
                pass

    def validate_disconnect(self, account, accounts):
        """Validate whether or not the socialaccount account can be safely disconnected.

        Honours other authentication backends, i.e. ignores unusable passwords if LDAP is used.
        """
        if "django_auth_ldap.backend.LDAPBackend" in settings.AUTHENTICATION_BACKENDS:
            # Ignore upstream validation error as we do not need a usable password
            return None

        # Let upstream decide whether we can disconnect or not
        return super().validate_disconnect(account, accounts)


class OurAccountAdapter(BaseInvitationsAdapter, DefaultAccountAdapter):
    """Customised adapter to support invitations and signup."""

    def is_open_for_signup(self, request):
        # We have an own signup form, so we deactivate allauth here
        return False

    def post_login(self, request, user, *args, **kwargs):
        resp = super().post_login(request, user, *args, **kwargs)
        sociallogin = (kwargs.get("signal_kwargs") or {}).get("sociallogin")
        redirect_url = get_login_redirect_url(
            request, kwargs["redirect_url"], signup=kwargs["signup"]
        )
        redirect_url = remove_prefix(redirect_url, "/django")
        if sociallogin:
            return HttpResponseRedirect(redirect_url)
        return resp

    def get_reset_password_from_key_url(self, key):
        return urljoin(settings.BASE_URL, f"/accounts/password/reset/key/{key}")
