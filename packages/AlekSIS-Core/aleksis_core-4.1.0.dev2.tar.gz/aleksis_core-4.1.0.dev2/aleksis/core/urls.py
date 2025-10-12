from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.urls import include, path, re_path
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog

import calendarweek.django
from ckeditor_uploader import views as ckeditor_uploader_views
from health_check.urls import urlpatterns as health_urls
from maintenance_mode.decorators import force_maintenance_mode_off
from oauth2_provider.views import ConnectDiscoveryInfoView
from rules.contrib.views import permission_required

from . import views

urlpatterns = [
    path(
        "",
        force_maintenance_mode_off(TemplateView.as_view(template_name="core/vue_index.html")),
        name="vue_app",
    ),
    path("manifest.json", views.ManifestView.as_view(), name="manifest"),
    path("sw.js", views.ServiceWorkerView.as_view(), name="service_worker"),
    path(settings.MEDIA_URL.removeprefix("/"), include("titofisto.urls")),
    path("__icons__/", include("dj_iconify.urls")),
    path(
        "graphql/",
        csrf_exempt(views.LoggingGraphQLView.as_view()),
        name="graphql",
    ),
    path("logo", force_maintenance_mode_off(views.LogoView.as_view()), name="logo"),
    path(
        ".well-known/openid-configuration",
        ConnectDiscoveryInfoView.as_view(),
        name="oidc_configuration",
    ),
    path(
        ".well-known/carddav/",
        views.DAVWellKnownView.as_view(),
        name="wellknown_carddav",
    ),
    path(
        ".well-known/caldav/",
        views.DAVWellKnownView.as_view(),
        name="wellknown_caldav",
    ),
    path("oauth/applications/", views.TemplateView.as_view(template_name="core/vue_index.html")),
    path(
        "oauth/applications/register/",
        views.TemplateView.as_view(template_name="core/vue_index.html"),
    ),
    path(
        "oauth/applications/<int:pk>/",
        views.TemplateView.as_view(template_name="core/vue_index.html"),
    ),
    path(
        "oauth/applications/<int:pk>/delete/",
        views.TemplateView.as_view(template_name="core/vue_index.html"),
    ),
    path(
        "oauth/applications/<int:pk>/edit/",
        views.TemplateView.as_view(template_name="core/vue_index.html"),
    ),
    path(
        "oauth/authorized_tokens/", views.TemplateView.as_view(template_name="core/vue_index.html")
    ),
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("system_status/", views.SystemStatusAPIView.as_view(), name="system_status_api"),
    path(
        "o/<str:app_label>/<str:model>/<uuid:pk>",
        views.ObjectRepresentationView.as_view(),
        name="object_representation_with_uuid",
    ),
    path(
        "o/<str:app_label>/<str:model>/<int:pk>",
        views.ObjectRepresentationView.as_view(),
        name="object_representation_with_pk",
    ),
    path(
        "o/",
        views.ObjectRepresentationView.as_view(),
        name="object_representation_anonymous",
    ),
    path(
        "feeds/<str:subregistry>/<str:name>.ics", views.ICalFeedView.as_view(), name="calendar_feed"
    ),
    path("feeds/<str:name>.ics", views.ICalAllFeedsView.as_view(), name="all_calendar_feeds"),
    path("dav/", views.DAVResourceView.as_view(), name="dav_registry"),
    path("dav/<str:name>/", views.DAVResourceView.as_view(), name="dav_subregistry"),
    path(
        "dav/<str:subregistry>/<str:name>/",
        views.DAVResourceView.as_view(),
        name="dav_resource",
    ),
    path(
        "dav/<str:subregistry>/<str:name>/<int:id>.ics",
        views.DAVSingleResourceView.as_view(),
        name="dav_resource_calendar",
    ),
    path(
        "dav/<str:subregistry>/<str:name>/<int:id>.vcf",
        views.DAVSingleResourceView.as_view(),
        name="dav_resource_contact",
    ),
    path("", include("django_prometheus.urls")),
    path(
        "django/",
        include(
            [
                path("accounts/login/", never_cache(views.LoginView.as_view()), name="login"),
                path("accounts/logout/", views.CustomLogoutView.as_view(), name="logout"),
                path(
                    "accounts/password/change/",
                    views.TemplateView.as_view(template_name="core/vue_index.html"),
                    name="account_change_password",
                ),
                path(
                    "accounts/password/reset/",
                    views.TemplateView.as_view(template_name="core/vue_index.html"),
                    name="account_reset_password",
                ),
                path(
                    "password/reset/done/",
                    views.TemplateView.as_view(template_name="core/vue_index.html"),
                    name="account_reset_password_done",
                ),
                path("accounts/", include("allauth.urls")),
                path(
                    "accounts/3rdparty/<int:pk>/delete/",
                    views.SocialAccountDeleteView.as_view(),
                    name="delete_social_account_by_pk",
                ),
                path("offline/", views.OfflineView.as_view(), name="offline"),
                path(
                    "invitations/send-invite/", views.InvitePerson.as_view(), name="invite_person"
                ),
                path(
                    "invitations/code/generate/",
                    views.GenerateInvitationCode.as_view(),
                    name="generate_invitation_code",
                ),
                path(
                    "invitations/disabled/",
                    views.InviteDisabledView.as_view(),
                    name="invite_disabled",
                ),
                path("invitations/", include("invitations.urls")),
                path(
                    "o/core/person/",
                    TemplateView.as_view(template_name="core/empty.html"),
                    name="persons",
                ),
                path(
                    "o/",
                    TemplateView.as_view(template_name="core/empty.html"),
                    name="person",
                ),
                path(
                    "o/core/person/<int:id_>",
                    TemplateView.as_view(template_name="core/empty.html"),
                    name="person_by_id",
                ),
                path(
                    "o/core/person/<int:pk>/invite/",
                    views.InvitePersonByID.as_view(),
                    name="invite_person_by_id",
                ),
                path(
                    "o/core/group/",
                    TemplateView.as_view(template_name="core/empty.html"),
                    name="groups",
                ),
                path("o/core/group/create/", views.edit_group, name="create_group"),
                path(
                    "o/core/group/<int:id_>",
                    TemplateView.as_view(template_name="core/empty.html"),
                    name="group_by_id",
                ),
                path("o/core/group/<int:id_>/edit/", views.edit_group, name="edit_group_by_id"),
                path("", TemplateView.as_view(template_name="core/vue_index.html"), name="index"),
                path("search/searchbar/", views.searchbar_snippets, name="searchbar_snippets"),
                path("search/", views.PermissionSearchView.as_view(), name="haystack_search"),
                path("maintenance-mode/", include("maintenance_mode.urls")),
                path("impersonate/", include("impersonate.urls")),
                path(
                    "oauth/authorize/",
                    views.CustomAuthorizationView.as_view(),
                    name="oauth2_provider:authorize",
                ),
                path("__i18n__/", include("django.conf.urls.i18n")),
                path(
                    "ckeditor/upload/",
                    permission_required("core.ckeditor_upload_files_rule")(
                        ckeditor_uploader_views.upload
                    ),
                    name="ckeditor_upload",
                ),
                path(
                    "ckeditor/browse/",
                    permission_required("core.ckeditor_upload_files_rule")(
                        ckeditor_uploader_views.browse
                    ),
                    name="ckeditor_browse",
                ),
                path("select2/", include("django_select2.urls")),
                path(
                    "calendarweek_i18n.js", calendarweek.django.i18n_js, name="calendarweek_i18n_js"
                ),
                path("gettext.js", JavaScriptCatalog.as_view(), name="javascript-catalog"),
                path(
                    "preferences/site/",
                    views.preferences,
                    {"registry_name": "site"},
                    name="preferences_site",
                ),
                path(
                    "preferences/person/",
                    views.preferences,
                    {"registry_name": "person"},
                    name="preferences_person",
                ),
                path(
                    "preferences/group/",
                    views.preferences,
                    {"registry_name": "group"},
                    name="preferences_group",
                ),
                path(
                    "preferences/person/<int:pk>/",
                    views.preferences,
                    {"registry_name": "person"},
                    name="preferences_person",
                ),
                path(
                    "preferences/group/<int:pk>/",
                    views.preferences,
                    {"registry_name": "group"},
                    name="preferences_group",
                ),
                path(
                    "preferences/person/<int:pk>/<str:section>/",
                    views.preferences,
                    {"registry_name": "person"},
                    name="preferences_person",
                ),
                path(
                    "preferences/group/<int:pk>/<str:section>/",
                    views.preferences,
                    {"registry_name": "group"},
                    name="preferences_group",
                ),
                path(
                    "preferences/site/<str:section>/",
                    views.preferences,
                    {"registry_name": "site"},
                    name="preferences_site",
                ),
                path(
                    "preferences/person/<str:section>/",
                    views.preferences,
                    {"registry_name": "person"},
                    name="preferences_person",
                ),
                path(
                    "preferences/group/<str:section>/",
                    views.preferences,
                    {"registry_name": "group"},
                    name="preferences_group",
                ),
                path("health/pdf/", views.TestPDFGenerationView.as_view(), name="test_pdf"),
                path("health/", include(health_urls)),
                path(
                    "permissions/global/user/",
                    views.UserGlobalPermissionsListBaseView.as_view(),
                    name="manage_user_global_permissions",
                ),
                path(
                    "permissions/global/group/",
                    views.GroupGlobalPermissionsListBaseView.as_view(),
                    name="manage_group_global_permissions",
                ),
                path(
                    "permissions/object/user/",
                    views.UserObjectPermissionsListBaseView.as_view(),
                    name="manage_user_object_permissions",
                ),
                path(
                    "permissions/object/group/",
                    views.GroupObjectPermissionsListBaseView.as_view(),
                    name="manage_group_object_permissions",
                ),
                path(
                    "permissions/global/user/<int:pk>/delete/",
                    views.UserGlobalPermissionDeleteView.as_view(),
                    name="delete_user_global_permission",
                ),
                path(
                    "permissions/global/group/<int:pk>/delete/",
                    views.GroupGlobalPermissionDeleteView.as_view(),
                    name="delete_group_global_permission",
                ),
                path(
                    "permissions/object/user/<int:pk>/delete/",
                    views.UserObjectPermissionDeleteView.as_view(),
                    name="delete_user_object_permission",
                ),
                path(
                    "permissions/object/group/<int:pk>/delete/",
                    views.GroupObjectPermissionDeleteView.as_view(),
                    name="delete_group_object_permission",
                ),
                path(
                    "permissions/assign/",
                    views.SelectPermissionForAssignView.as_view(),
                    name="select_permission_for_assign",
                ),
                path(
                    "permissions/<int:pk>/assign/",
                    views.AssignPermissionView.as_view(),
                    name="assign_permission",
                ),
            ]
        ),
    ),
]

# Use custom server error handler to get a request object in the template
handler500 = views.server_error

# Automatically mount URLs from all installed AlekSIS apps
for app_config in apps.app_configs.values():
    if not app_config.name.startswith("aleksis.apps."):
        continue

    try:
        urls_module = import_module(f"{app_config.name}.urls")
    except ModuleNotFoundError:
        # Ignore exception as app just has no URLs
        urls_module = None

    if hasattr(urls_module, "urlpatterns"):
        urlpatterns.append(
            path(f"django/app/{app_config.label}/", include(urls_module.urlpatterns))
        )

    if hasattr(urls_module, "api_urlpatterns"):
        urlpatterns.append(path(f"app/{app_config.label}/", include(urls_module.api_urlpatterns)))

    if hasattr(urls_module, "wellknown_urlpatterns"):
        urlpatterns.append(path(".well-known/", include(urls_module.wellknown_urlpatterns)))

urlpatterns.append(
    re_path(
        r"^(?P<url>.*)/$",
        force_maintenance_mode_off(TemplateView.as_view(template_name="core/vue_index.html")),
        name="vue_app",
    )
)
