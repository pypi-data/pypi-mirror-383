from typing import TYPE_CHECKING, Any, Optional

import django.apps
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import gettext as _

from dynamic_preferences.registries import preference_models
from health_check.plugins import plugin_dir
from oauthlib.common import Request as OauthlibRequest

from .registries import group_preferences_registry, person_preferences_registry
from .util.apps import AppConfig
from .util.core_helpers import (
    create_default_celery_schedule,
    get_or_create_favicon,
    get_site_preferences,
    has_person,
)
from .util.types import setup_types

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class CoreConfig(AppConfig):
    name = "aleksis.core"
    verbose_name = "AlekSIS — The Free School Information System"
    dist_name = "AlekSIS-Core"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/official/AlekSIS/",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        (
            [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
            "Jonathan Weth",
            "dev@jonathanweth.de",
        ),
        ([2017, 2018, 2019, 2020], "Frank Poetzsch-Heffter", "p-h@katharineum.de"),
        ([2018, 2019, 2020, 2021, 2022, 2023, 2024], "Hangzhi Yu", "yuha@katharineum.de"),
        ([2018, 2019, 2020, 2021, 2022, 2023, 2024], "Julian Leucker", "leuckeju@katharineum.de"),
        (
            [2019, 2020, 2021, 2022, 2023, 2024, 2025],
            "Dominik George",
            "dominik.george@teckids.org",
        ),
        ([2019, 2020, 2021, 2022], "Tom Teichler", "tom.teichler@teckids.org"),
        ([2019], "mirabilos", "thorsten.glaser@teckids.org"),
        ([2021, 2022, 2023, 2024], "magicfelix", "felix@felix-zauberer.de"),
        ([2021], "Lloyd Meins", "meinsll@katharineum.de"),
        ([2022], "Benedict Suska", "benedict.suska@teckids.org"),
        ([2022, 2023, 2024], "Lukas Weichelt", "lukas.weichelt@teckids.org"),
        ([2023, 2024], "Michael Bauer", "michael-bauer@posteo.de"),
        ([2024], "Jonathan Krüger", "jonathan.krueger@teckids.org"),
    )

    def ready(self):
        super().ready()

        setup_types()

        from django.conf import settings  # noqa

        # Autodiscover various modules defined by AlekSIS
        autodiscover_modules("model_extensions", "form_extensions", "checks", "util.dav_handler")

        personpreferencemodel = self.get_model("PersonPreferenceModel")
        grouppreferencemodel = self.get_model("GroupPreferenceModel")

        preference_models.register(personpreferencemodel, person_preferences_registry)
        preference_models.register(grouppreferencemodel, group_preferences_registry)

        from .health_checks import (
            BackupJobHealthCheck,
            DataChecksHealthCheckBackend,
            DbBackupAgeHealthCheck,
            MediaBackupAgeHealthCheck,
        )

        plugin_dir.register(DataChecksHealthCheckBackend)
        plugin_dir.register(DbBackupAgeHealthCheck)
        plugin_dir.register(MediaBackupAgeHealthCheck)
        plugin_dir.register(BackupJobHealthCheck)

    def preference_updated(
        self,
        sender: Any,
        section: Optional[str] = None,
        name: Optional[str] = None,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        **kwargs,
    ) -> None:
        from django.conf import settings  # noqa

        if section == "theme" and name in ("favicon", "pwa_icon"):
            from favicon.models import Favicon, FaviconImg  # noqa

            is_favicon = name == "favicon"

            if new_value:
                # Get file object from preferences instead of using new_value
                # to prevent problems with special file storages
                file_obj = get_site_preferences()[f"{section}__{name}"]

                favicon = Favicon.objects.update_or_create(
                    title=name,
                    defaults={"isFavicon": is_favicon, "faviconImage": file_obj},
                )[0]
                FaviconImg.objects.filter(faviconFK=favicon).delete()
            else:
                Favicon.objects.filter(title=name, isFavicon=is_favicon).delete()
                if name in settings.DEFAULT_FAVICON_PATHS:
                    get_or_create_favicon(
                        name, settings.DEFAULT_FAVICON_PATHS[name], is_favicon=is_favicon
                    )

    def pre_migrate(
        self,
        app_config: django.apps.AppConfig,
        verbosity: int,
        interactive: bool,
        using: str,
        plan: list[tuple],
        apps: django.apps.registry.Apps,
        **kwargs,
    ) -> None:
        super().pre_migrate(app_config, verbosity, interactive, using, plan, apps)
        from .data_checks import check_data_for_migrations

        # Run data checks to validate data
        check_data_for_migrations(with_dependencies=True)

    def post_migrate(
        self,
        app_config: django.apps.AppConfig,
        verbosity: int,
        interactive: bool,
        using: str,
        **kwargs,
    ) -> None:
        from django.conf import settings  # noqa
        from .data_checks import check_data_for_migrations

        super().post_migrate(app_config, verbosity, interactive, using, **kwargs)

        # Ensure that default Favicon object exists
        for name, default in settings.DEFAULT_FAVICON_PATHS.items():
            get_or_create_favicon(name, default, is_favicon=name == "favicon")

        # Create default periodic tasks
        create_default_celery_schedule()

        # Run data checks to validate data
        check_data_for_migrations()

    def user_logged_in(
        self, sender: type, request: Optional[HttpRequest], user: "User", **kwargs
    ) -> None:
        if has_person(user):
            # Save the associated person to pick up defaults
            user.person.save()

    def user_logged_out(
        self, sender: type, request: Optional[HttpRequest], user: "User", **kwargs
    ) -> None:
        messages.success(request, _("You have been logged out successfully."))

    @classmethod
    def get_all_scopes(cls) -> dict[str, str]:
        scopes = {
            "read": "Read anything the resource owner can read",
            "write": "Write anything the resource owner can write",
        }
        if settings.OAUTH2_PROVIDER.get("OIDC_ENABLED", False):
            scopes |= {
                "openid": _("OpenID Connect scope"),
                "profile": _("Given name, family name, link to profile and picture if existing."),
                "addresses": _("Postal addresses"),
                "email": _("Email address"),
                "phone": _("Home and mobile phone"),
                "groups": _("Groups"),
            }
        return scopes

    @classmethod
    def get_additional_claims(cls, scopes: list[str], request: OauthlibRequest) -> dict[str, Any]:
        django_request = HttpRequest()
        django_request.META = request.headers

        claims = {
            "preferred_username": request.user.username,
        }

        if "profile" in scopes:
            if has_person(request.user):
                claims["given_name"] = request.user.person.first_name
                claims["family_name"] = request.user.person.last_name
                claims["profile"] = django_request.build_absolute_uri(
                    request.user.person.get_absolute_url()
                )
                if request.user.person.avatar:
                    claims["picture"] = django_request.build_absolute_uri(
                        request.user.person.avatar.url
                    )
            else:
                claims["given_name"] = request.user.first_name
                claims["family_name"] = request.user.last_name

        if "email" in scopes:
            if has_person(request.user):
                claims["email"] = request.user.person.email
            else:
                claims["email"] = request.user.email

        if "addresses" in scopes and has_person(request.user):
            claims["addresses"] = [
                {
                    "street_address": address.street + " " + address.housenumber,
                    "locality": address.place,
                    "postal_code": address.postal_code,
                }
                for address in request.user.person.addresses.all()
            ]

        if "phone" in scopes and has_person(request.user):
            claims["mobile_number"] = request.user.person.mobile_number
            claims["phone_number"] = request.user.person.phone_number

        if "groups" in scopes and has_person(request.user):
            claims["groups"] = list(
                request.user.person.member_of.values_list("name", flat=True).all()
            )

        return claims
