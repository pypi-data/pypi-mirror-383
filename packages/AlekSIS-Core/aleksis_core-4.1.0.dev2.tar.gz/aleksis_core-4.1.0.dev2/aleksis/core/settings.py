import os
import warnings
from copy import deepcopy
from glob import glob
from socket import getfqdn

from django.utils.log import DEFAULT_LOGGING
from django.utils.translation import gettext_lazy as _

from dynaconf import LazySettings

from .util.core_helpers import (
    get_app_packages,
    get_app_settings_overrides,
    lazy_preference,
    merge_app_settings,
    monkey_patch,
)

monkey_patch()

IN_PYTEST = "PYTEST_CURRENT_TEST" in os.environ or "TOX_ENV_DIR" in os.environ
PYTEST_SETUP_DATABASES = [("default", "default_oot")]

ENVVAR_PREFIX_FOR_DYNACONF = "ALEKSIS"
DIRS_FOR_DYNACONF = ["/etc/aleksis"]
MERGE_ENABLED_FOR_DYNACONF = True

SETTINGS_FILE_FOR_DYNACONF = []
for directory in DIRS_FOR_DYNACONF:
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*.json"))
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*.ini"))
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*.yaml"))
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*.toml"))
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*/*.json"))
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*/*.ini"))
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*/*.yaml"))
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*/*.toml"))

_settings = LazySettings(
    ENVVAR_PREFIX_FOR_DYNACONF=ENVVAR_PREFIX_FOR_DYNACONF,
    SETTINGS_FILE_FOR_DYNACONF=SETTINGS_FILE_FOR_DYNACONF,
    MERGE_ENABLED_FOR_DYNACONF=MERGE_ENABLED_FOR_DYNACONF,
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cache directory for external operations
CACHE_DIR = _settings.get("caching.dir", os.path.join(BASE_DIR, "cache"))

SILENCED_SYSTEM_CHECKS = []

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = _settings.get("secret_key", "DoNotUseInProduction")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _settings.get("maintenance.debug", False)
INTERNAL_IPS = _settings.get("maintenance.internal_ips", [])

UWSGI = {
    "module": "aleksis.core.wsgi",
}
UWSGI_SERVE_STATIC = True
UWSGI_SERVE_MEDIA = False
if DEBUG and "UWSGI_WORKERS" not in os.environ:
    UWSGI["cheaper"] = 0
    UWSGI["workers"] = 1

DEV_SERVER_PORT = 8000
DJANGO_VITE_DEV_SERVER_PORT = DEV_SERVER_PORT + 1

ALLOWED_HOSTS = _settings.get("http.allowed_hosts", [getfqdn(), "localhost", "127.0.0.1", "[::1]"])
BASE_URL = _settings.get(
    "http.base_url",
    f"http://localhost:{DEV_SERVER_PORT}" if DEBUG else f"https://{ALLOWED_HOSTS[0]}",
)


def generate_trusted_origins():
    origins = []
    origins += [f"http://{host}" for host in ALLOWED_HOSTS]
    origins += [f"https://{host}" for host in ALLOWED_HOSTS]
    if DEBUG:
        origins += [f"http://{host}:{DEV_SERVER_PORT}" for host in ALLOWED_HOSTS]
        origins += [f"http://{host}:{DJANGO_VITE_DEV_SERVER_PORT}" for host in ALLOWED_HOSTS]
    return origins


CSRF_TRUSTED_ORIGINS = _settings.get("http.trusted_origins", generate_trusted_origins())

# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_uwsgi",
    "django_extensions",
    "guardian",
    "rules.apps.AutodiscoverRulesConfig",
    "haystack",
    "polymorphic",
    "dbbackup",
    "django_celery_beat",
    "django_celery_results",
    "celery_progress",
    "health_check.contrib.celery",
    "djcelery_email",
    "celery_haystack",
    "django_any_js",
    "django_yarnpkg",
    "django_vite",
    "django_tables2",
    "maintenance_mode",
    "reversion",
    "phonenumber_field",
    "django_prometheus",
    "django.contrib.admin",
    "django_select2",
    "templated_email",
    "html2text",
    "aleksis.core",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    "invitations",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.psutil",
    "health_check.contrib.migrations",
    "dynamic_preferences",
    "dynamic_preferences.users.apps.UserPreferencesConfig",
    "impersonate",
    "material",
    "ckeditor",
    "ckeditor_uploader",
    "colorfield",
    "django_bleach",
    "favicon",
    "django_filters",
    "oauth2_provider",
    "rest_framework",
    "graphene_django",
    "dj_iconify.apps.DjIconifyConfig",
    "recurrence",
]

merge_app_settings("INSTALLED_APPS", INSTALLED_APPS, True)
INSTALLED_APPS += get_app_packages()

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

MIDDLEWARE = [
    #    'django.middleware.cache.UpdateCacheMiddleware',
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "impersonate.middleware.ImpersonateMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "maintenance_mode.middleware.MaintenanceModeMiddleware",
    "aleksis.core.util.middlewares.EnsurePersonMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    #    'django.middleware.cache.FetchFromCacheMiddleware'
]

ROOT_URLCONF = "aleksis.core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "maintenance_mode.context_processors.maintenance_mode",
                "dynamic_preferences.processors.global_preferences",
                "aleksis.core.util.core_helpers.custom_information_processor",
                "aleksis.core.util.context_processors.need_maintenance_response_context_processor",
            ],
        },
    },
]

# Attention: The following context processors must accept None
# as first argument (in addition to a HttpRequest object)
NON_REQUEST_CONTEXT_PROCESSORS = [
    "django.template.context_processors.i18n",
    "django.template.context_processors.tz",
    "aleksis.core.util.core_helpers.custom_information_processor",
]

WSGI_APPLICATION = "aleksis.core.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": _settings.get("database.name", "aleksis"),
        "USER": _settings.get("database.username", "aleksis"),
        "PASSWORD": _settings.get("database.password", None),
        "HOST": _settings.get("database.host", "127.0.0.1"),
        "PORT": _settings.get("database.port", "5432"),
        "OPTIONS": _settings.get("database.options", {}),
        "ATOMIC_REQUESTS": True,
    }
}

# Configure PostgreSQL connection pool with defaults if not custom
if "pool" not in DATABASES["default"]["OPTIONS"] and not _settings.get(
    "database.disable_pool", False
):
    DATABASES["default"]["OPTIONS"]["pool"] = {
        "min_size": 5,
        "max_size": 20,
        "timeout": 5,
    }

if _settings.get("database.conn_max_age", None) is not None:
    DATABASES["default"]["OPTIONS"]["pool"]["max_lifetime"] = _settings.get("database.conn_max_age")

# Duplicate default database for out-of-transaction updates
DATABASES["default_oot"] = DATABASES["default"].copy()
DATABASE_ROUTERS = [
    "aleksis.core.util.core_helpers.OOTRouter",
]
DATABASE_OOT_LABELS = ["django_celery_results"]

merge_app_settings("DATABASES", DATABASES, False)

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.ScryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

_VALKEY = _settings.get("valkey", {})
_VALKEY.update(_settings.get("redis", {}))

VALKEY_HOST = REDIS_HOST = _VALKEY.get("host", "localhost")
VALKEY_PORT = REDIS_PORT = _VALKEY.get("port", 6379)
VALKEY_DB = REDIS_DB = _VALKEY.get("database", 0)
VALKEY_PASSWORD = REDIS_PASSWORD = _VALKEY.get("password", None)
VALKEY_USER = REDIS_USER = _VALKEY.get("user", None if VALKEY_PASSWORD is None else "default")

VALKEY_URL = REDIS_URL = (
    f"redis://{VALKEY_USER + ':' + VALKEY_PASSWORD + '@' if VALKEY_USER else ''}"
    f"{VALKEY_HOST}:{VALKEY_PORT}/{VALKEY_DB}"
)

if _settings.get("caching.valkey.enabled", _settings.get("caching.redis.enabled", not IN_PYTEST)):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": _settings.get(
                "caching.valkey.address", _settings.get("caching.redis.address", VALKEY_URL)
            ),
        }
    }
else:
    CACHES = {
        "default": {
            # Use uWSGI if available (will auot-fallback to LocMemCache)
            "BACKEND": "django_uwsgi.cache.UwsgiCache"
        }
    }


SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_INITIAL_SUPERUSER = {
    "username": _settings.get("auth.superuser.username", "admin"),
    "password": _settings.get("auth.superuser.password", "admin"),
    "email": _settings.get("auth.superuser.email", "root@example.com"),
}

# Authentication backends are dynamically populated
AUTHENTICATION_BACKENDS = []

# Configuration for django-allauth.

# Use custom adapter to override some behaviour, i.e. honour the LDAP backend
SOCIALACCOUNT_ADAPTER = "aleksis.core.util.auth_adapters.OurSocialAccountAdapter"

# Get django-allauth providers from config
_SOCIALACCOUNT_PROVIDERS = _settings.get("auth.providers", None)
if _SOCIALACCOUNT_PROVIDERS:
    SOCIALACCOUNT_PROVIDERS = _SOCIALACCOUNT_PROVIDERS.to_dict()

    # Add configured social auth providers to INSTALLED_APPS
    for provider, config in SOCIALACCOUNT_PROVIDERS.items():
        INSTALLED_APPS.append(f"allauth.socialaccount.providers.{provider}")
        SOCIALACCOUNT_PROVIDERS[provider] = {k.upper(): v for k, v in config.items()}

ALEKSIS_SOCIALACCOUNT_USERNAME_MATCHING = _settings.get(
    "auth.socialaccount_username_matching", False
)

# django-allauth[mfa]

MFA_SUPPORTED_TYPES = ["recovery_codes", "totp", "webauthn"]
MFA_TOTP_ISSUER = lazy_preference("general", "title")
MFA_TRUST_ENABLED = _settings.get("mfa.trust.enabled")

# Configure custom forms

ACCOUNT_FORMS = {
    "signup": "aleksis.core.forms.AccountRegisterForm",
}

# Use custom adapter
ACCOUNT_ADAPTER = "aleksis.core.util.auth_adapters.OurAccountAdapter"
INVITATIONS_ADAPTER = "aleksis.core.util.auth_adapters.OurAccountAdapter"

# Require password confirmation
SIGNUP_PASSWORD_ENTER_TWICE = True

# Allow login by either username or email
ACCOUNT_AUTHENTICATION_METHOD = _settings.get("auth.registration.method", "username_email")

# Require email address to sign up
ACCOUNT_EMAIL_REQUIRED = _settings.get("auth.registration.email_required", True)
SOCIALACCOUNT_EMAIL_REQUIRED = False

# Rate limiting for verification emails and login
ACCOUNT_RATE_LIMITS = {
    "confirm_email": _settings.get("auth.limits.confirm_email", "1/3m/key"),
    "login_failed": _settings.get("auth.limits.login_failed", "10/m/ip,5/5m/key"),
}

# Require email verification after sign up
ACCOUNT_EMAIL_VERIFICATION = _settings.get("auth.registration.email_verification", "optional")
SOCIALACCOUNT_EMAIL_VERIFICATION = False

# Email subject prefix for verification mails
ACCOUNT_EMAIL_SUBJECT_PREFIX = _settings.get("auth.registration.subject", "[AlekSIS] ")

# Enforce uniqueness of email addresses
ACCOUNT_UNIQUE_EMAIL = _settings.get("auth.registration.unique_email", True)

# Configurable username validators
ACCOUNT_USERNAME_VALIDATORS = "aleksis.core.util.auth_helpers.custom_username_validators"

ACCOUNT_SESSION_REMEMBER = False

# Don't send emails to unknown accounts on password reset
ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False

# Configuration for django-invitations

# Expire invitations are configured amout of days
INVITATIONS_INVITATION_EXPIRY = _settings.get("auth.invitation.expiry", 3)
# Use email prefix configured for django-allauth
INVITATIONS_EMAIL_SUBJECT_PREFIX = ACCOUNT_EMAIL_SUBJECT_PREFIX
# Use custom invitation model
INVITATIONS_INVITATION_MODEL = "core.PersonInvitation"
# Use custom invitation form
INVITATIONS_INVITE_FORM = "aleksis.core.forms.PersonCreateInviteForm"
# Display error message if invitation code is invalid
INVITATIONS_GONE_ON_ACCEPT_ERROR = False

# Configuration for OAuth2 provider
OAUTH2_PROVIDER = {
    "SCOPES_BACKEND_CLASS": "aleksis.core.util.auth_helpers.AppScopes",
    "OAUTH2_VALIDATOR_CLASS": "aleksis.core.util.auth_helpers.CustomOAuth2Validator",
    "OIDC_ENABLED": True,
    "OIDC_ISS_ENDPOINT": BASE_URL,
    "OIDC_RP_INITIATED_LOGOUT_ENABLED": True,
    "OIDC_RP_INITIATED_LOGOUT_ALWAYS_PROMPT": True,
    "REFRESH_TOKEN_EXPIRE_SECONDS": _settings.get("oauth2.token_expiry", 86400),
    "PKCE_REQUIRED": False,
}
OAUTH2_PROVIDER_APPLICATION_MODEL = "core.OAuthApplication"
OAUTH2_PROVIDER_GRANT_MODEL = "core.OAuthGrant"
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = "core.OAuthAccessToken"  # noqa: S105
OAUTH2_PROVIDER_ID_TOKEN_MODEL = "core.OAuthIDToken"  # noqa: S105
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = "core.OAuthRefreshToken"  # noqa: S105

_OIDC_RSA_KEY_DEFAULT = "/etc/aleksis/oidc.pem"
_OIDC_RSA_KEY = _settings.get("oauth2.oidc.rsa_key", "/etc/aleksis/oidc.pem")
if "BEGIN RSA PRIVATE KEY" in _OIDC_RSA_KEY:
    OAUTH2_PROVIDER["OIDC_RSA_PRIVATE_KEY"] = _OIDC_RSA_KEY
elif _OIDC_RSA_KEY == _OIDC_RSA_KEY_DEFAULT and not os.path.exists(_OIDC_RSA_KEY):
    warnings.warn(
        (
            f"The default OIDC RSA key in {_OIDC_RSA_KEY} does not exist. "
            f"RSA will be disabled for now, but creating and configuring a "
            f"key is recommended. To silence this warning, set oauth2.oidc.rsa_key "
            f"to the empty string in a configuration file."
        )
    )
elif _OIDC_RSA_KEY:
    with open(_OIDC_RSA_KEY, "r") as f:
        OAUTH2_PROVIDER["OIDC_RSA_PRIVATE_KEY"] = f.read()

# Configuration for REST framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}
OBJECT_REPR_USE_FRONTEND = True

# Configuration for GraphQL framework
GRAPHENE = {"SCHEMA": "aleksis.core.schema.schema", "TESTING_ENDPOINT": "/graphql/"}

# LDAP config
if _settings.get("ldap.uri", None):
    # LDAP dependencies are not necessarily installed, so import them here
    import ldap  # noqa
    from django_auth_ldap.config import (
        LDAPSearch,
        LDAPSearchUnion,
        NestedGroupOfNamesType,
        NestedGroupOfUniqueNamesType,
        PosixGroupType,
    )

    AUTH_LDAP_GLOBAL_OPTIONS = {
        ldap.OPT_NETWORK_TIMEOUT: _settings.get("ldap.network_timeout", 3),
    }

    # Enable Django's integration to LDAP
    AUTHENTICATION_BACKENDS.append("aleksis.core.util.ldap.LDAPBackend")

    AUTH_LDAP_SERVER_URI = _settings.get("ldap.uri")

    # Optional: non-anonymous bind
    if _settings.get("ldap.bind.dn", None):
        AUTH_LDAP_BIND_DN = _settings.get("ldap.bind.dn")
        AUTH_LDAP_BIND_PASSWORD = _settings.get("ldap.bind.password")

    # Keep local password for users to be required to provide their old password on change
    AUTH_LDAP_SET_USABLE_PASSWORD = _settings.get("ldap.handle_passwords", True)

    # Keep bound as the authenticating user
    # Ensures proper read permissions, and ability to change password without admin
    AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True

    # The TOML config might contain either one table or an array of tables
    _AUTH_LDAP_USER_SETTINGS = _settings.get("ldap.users.search")
    if not isinstance(_AUTH_LDAP_USER_SETTINGS, list):
        _AUTH_LDAP_USER_SETTINGS = [_AUTH_LDAP_USER_SETTINGS]

    # Search attributes to find users by username
    AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
        *[
            LDAPSearch(
                entry["base"],
                ldap.SCOPE_SUBTREE,
                entry.get("filter", "(uid=%(user)s)"),
            )
            for entry in _AUTH_LDAP_USER_SETTINGS
        ]
    )

    # Mapping of LDAP attributes to Django model fields
    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": _settings.get("ldap.users.map.first_name", "givenName"),
        "last_name": _settings.get("ldap.users.map.last_name", "sn"),
        "email": _settings.get("ldap.users.map.email", "mail"),
    }

    # Discover flags by LDAP groups
    if _settings.get("ldap.groups.search", None):
        group_type = _settings.get("ldap.groups.type", "groupOfNames")

        # The TOML config might contain either one table or an array of tables
        _AUTH_LDAP_GROUP_SETTINGS = _settings.get("ldap.groups.search")
        if not isinstance(_AUTH_LDAP_GROUP_SETTINGS, list):
            _AUTH_LDAP_GROUP_SETTINGS = [_AUTH_LDAP_GROUP_SETTINGS]

        AUTH_LDAP_GROUP_SEARCH = LDAPSearchUnion(
            *[
                LDAPSearch(
                    entry["base"],
                    ldap.SCOPE_SUBTREE,
                    entry.get("filter", f"(objectClass={group_type})"),
                )
                for entry in _AUTH_LDAP_GROUP_SETTINGS
            ]
        )

        _group_type = _settings.get("ldap.groups.type", "groupOfNames").lower()
        if _group_type == "groupofnames":
            AUTH_LDAP_GROUP_TYPE = NestedGroupOfNamesType()
        elif _group_type == "groupofuniquenames":
            AUTH_LDAP_GROUP_TYPE = NestedGroupOfUniqueNamesType()
        elif _group_type == "posixgroup":
            AUTH_LDAP_GROUP_TYPE = PosixGroupType()

        AUTH_LDAP_USER_FLAGS_BY_GROUP = {}
        for _flag in ["is_active", "is_staff", "is_superuser"]:
            _dn = _settings.get(f"ldap.groups.flags.{_flag}", None)
            if _dn:
                AUTH_LDAP_USER_FLAGS_BY_GROUP[_flag] = _dn

        # Backend admin requires superusers to also be staff members
        if (
            "is_superuser" in AUTH_LDAP_USER_FLAGS_BY_GROUP
            and "is_staff" not in AUTH_LDAP_USER_FLAGS_BY_GROUP
        ):
            AUTH_LDAP_USER_FLAGS_BY_GROUP["is_staff"] = AUTH_LDAP_USER_FLAGS_BY_GROUP[
                "is_superuser"
            ]

# Add ModelBackend last so all other backends get a chance
# to verify passwords first
AUTHENTICATION_BACKENDS.append("django.contrib.auth.backends.ModelBackend")

# Authentication backend for django-allauth.
AUTHENTICATION_BACKENDS.append("allauth.account.auth_backends.AuthenticationBackend")

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGES = [
    ("en", _("English")),
    ("de", _("German")),
    ("uk", _("Ukrainian")),
]
LANGUAGE_CODE = _settings.get("l10n.lang", "en")
TIME_ZONE = _settings.get("l10n.tz", "UTC")
USE_TZ = True

PHONENUMBER_DEFAULT_REGION = _settings.get("l10n.phone_number_country", None)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/


STATIC_URL = _settings.get("static.url", "/static/")
MEDIA_URL = _settings.get("media.url", "/media/")

LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "index"

STATIC_ROOT = _settings.get("static.root", os.path.join(BASE_DIR, "static"))
MEDIA_ROOT = _settings.get("media.root", os.path.join(BASE_DIR, "media"))
NODE_MODULES_ROOT = CACHE_DIR

YARN_INSTALLED_APPS = [
    "@fontsource/roboto@^4.5.5",
    "jquery@^3.6.0",
    "@materializecss/materialize@~1.0.0",
    "material-design-icons-iconfont@^6.7.0",
    "select2-materialize@^0.1.8",
    "paper-css@^0.4.1",
    "jquery-sortablejs@^1.0.1",
    "sortablejs@^1.15.0",
    "@sentry/tracing@^7.28.0",
    "@iconify/iconify@^2.2.1",
    "@iconify/json@^2.1.30",
    "@mdi/font@^7.2.96",
    "@apollo/client@^3.13.8",
    "apollo3-cache-persist@^0.15.0",
    "apollo-link-sentry@^3.2.3",
    "deepmerge@^4.2.2",
    "graphql@^16.10.0",
    "graphql-tag@^2.12.6",
    "sass@^1.32",
    "vue@^3.5.13",
    "@vue/compat@^3.1.0",
    "@vue/apollo-option@^4.2.2",
    "@vue/apollo-components@^4.2.2",
    "@vue/apollo-composable@^4.2.2",
    "@vue/apollo-util@^4.2.2",
    "vuetify@^3.9.0",
    "vue-router@^4.5.1",
    "vue-cookies@^1.8.6",
    "vite@^6.3.5",
    "vite-plugin-pwa@^0.21.2",
    "vite-plugin-top-level-await@^1.2.2",
    "vite-plugin-vuetify@^2.1.1",
    "@vue/devtools-api@^7.7.6",
    "@vitejs/plugin-vue@^5.2.3",
    "@rollup/plugin-node-resolve@^15.0.1",
    "@rollup/plugin-graphql@^2.0.2",
    "@rollup/plugin-virtual@^3.0.1",
    "rollup-plugin-license@^3.0.1",
    "vue-i18n@11",
    "browserslist-to-esbuild@^1.2.0",
    "vite-plugin-browserslist-useragent@^0.4.1",
    "@sentry/vue@^9.15.0",
    "vue-draggable-grid@^1.0.2",
    "rrule",
    "luxon@^3.4.3",
    "apollo-upload-client@^18.0.1",
    "@vitejs/plugin-legacy@^6.0.0",
    "terser@^5.37.0",
    "graphql-combine-query@^1.2.4",
    "@github/webauthn-json@^2.1.1",
    "pinia@^3.0.2",
    "@material/material-color-utilities@^0.3.0",
    "@vueuse/core@^13.3.0",
    "@date-io/luxon@^3.2.0",
    "estree-toolkit@^1.7.13",
    "estree-util-value-to-estree@^3.4.0",
    "astring@^1.9.0",
]

merge_app_settings("YARN_INSTALLED_APPS", YARN_INSTALLED_APPS, True)

JS_URL = _settings.get("js_assets.url", STATIC_URL)
JS_ROOT = _settings.get("js_assets.root", os.path.join(NODE_MODULES_ROOT, "node_modules"))

DJANGO_VITE_ASSETS_PATH = os.path.join(NODE_MODULES_ROOT, "vite_bundles")
DJANGO_VITE_DEV_MODE = DEBUG

STATICFILES_DIRS = (
    DJANGO_VITE_ASSETS_PATH,
    JS_ROOT,
)

ANY_JS = {
    "materialize": {"js_url": JS_URL + "/@materializecss/materialize/dist/js/materialize.min.js"},
    "jQuery": {"js_url": JS_URL + "/jquery/dist/jquery.min.js"},
    "material-design-icons": {
        "css_url": JS_URL + "/material-design-icons-iconfont/dist/material-design-icons.css"
    },
    "paper-css": {"css_url": JS_URL + "/paper-css/paper.min.css"},
    "select2-materialize": {
        "css_url": JS_URL + "/select2-materialize/select2-materialize.css",
        "js_url": JS_URL + "/select2-materialize/index.js",
    },
    "sortablejs": {"js_url": JS_URL + "/sortablejs/Sortable.min.js"},
    "jquery-sortablejs": {"js_url": JS_URL + "/jquery-sortablejs/jquery-sortable.js"},
    "Roboto100": {"css_url": JS_URL + "/@fontsource/roboto/100.css"},
    "Roboto300": {"css_url": JS_URL + "/@fontsource/roboto/300.css"},
    "Roboto400": {"css_url": JS_URL + "/@fontsource/roboto/400.css"},
    "Roboto500": {"css_url": JS_URL + "/@fontsource/roboto/500.css"},
    "Roboto700": {"css_url": JS_URL + "/@fontsource/roboto/700.css"},
    "Roboto900": {"css_url": JS_URL + "/@fontsource/roboto/900.css"},
    "Sentry": {"js_url": JS_URL + "/@sentry/tracing/build/bundle.tracing.js"},
    "luxon": {"js_url": JS_URL + "/luxon/build/global/luxon.min.js"},
    "iconify": {"js_url": JS_URL + "/@iconify/iconify/dist/iconify.min.js"},
}

merge_app_settings("ANY_JS", ANY_JS, True)

ICONIFY_JSON_ROOT = os.path.join(JS_ROOT, "@iconify", "json")
ICONIFY_COLLECTIONS_ALLOWED = ["mdi"]

ADMINS = _settings.get(
    "contact.admins", [(AUTH_INITIAL_SUPERUSER["username"], AUTH_INITIAL_SUPERUSER["email"])]
)
SERVER_EMAIL = _settings.get("contact.from", ADMINS[0][1])
DEFAULT_FROM_EMAIL = _settings.get("contact.from", ADMINS[0][1])
MANAGERS = _settings.get("contact.admins", ADMINS)

if _settings.get("mail.server.host", None):
    EMAIL_HOST = _settings.get("mail.server.host")
    EMAIL_USE_TLS = _settings.get("mail.server.tls", False)
    EMAIL_USE_SSL = _settings.get("mail.server.ssl", False)
    if _settings.get("mail.server.port", None):
        EMAIL_PORT = _settings.get("mail.server.port")
    if _settings.get("mail.server.user", None):
        EMAIL_HOST_USER = _settings.get("mail.server.user")
        EMAIL_HOST_PASSWORD = _settings.get("mail.server.password")

TEMPLATED_EMAIL_BACKEND = "templated_email.backends.vanilla_django"
TEMPLATED_EMAIL_AUTO_PLAIN = True

DYNAMIC_PREFERENCES = {
    "REGISTRY_MODULE": "preferences",
}

MAINTENANCE_MODE = _settings.get("maintenance.enabled", None)
MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = _settings.get(
    "maintenance.ignore_ips", _settings.get("maintenance.internal_ips", [])
)
MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = "aleksis.core.util.core_helpers.get_ip"
MAINTENANCE_MODE_IGNORE_SUPERUSER = True
MAINTENANCE_MODE_STATE_FILE_NAME = _settings.get(
    "maintenance.statefile", "maintenance_mode_state.txt"
)
MAINTENANCE_MODE_STATE_BACKEND = "maintenance_mode.backends.DefaultStorageBackend"

DBBACKUP_STORAGE = _settings.get("backup.storage", "django.core.files.storage.FileSystemStorage")
DBBACKUP_STORAGE_OPTIONS = {"location": _settings.get("backup.location", "/var/backups/aleksis")}
DBBACKUP_CLEANUP_KEEP = _settings.get("backup.database.keep", 10)
DBBACKUP_CLEANUP_KEEP_MEDIA = _settings.get("backup.media.keep", 10)
DBBACKUP_GPG_RECIPIENT = _settings.get("backup.gpg_recipient", None)
DBBACKUP_COMPRESS_DB = _settings.get("backup.database.compress", True)
DBBACKUP_ENCRYPT_DB = _settings.get("backup.database.encrypt", DBBACKUP_GPG_RECIPIENT is not None)
DBBACKUP_COMPRESS_MEDIA = _settings.get("backup.media.compress", True)
DBBACKUP_ENCRYPT_MEDIA = _settings.get("backup.media.encrypt", DBBACKUP_GPG_RECIPIENT is not None)
DBBACKUP_CLEANUP_DB = _settings.get("backup.database.clean", True)
DBBACKUP_CLEANUP_MEDIA = _settings.get("backup.media.clean", True)
DBBACKUP_CONNECTOR_MAPPING = {
    "django_prometheus.db.backends.postgresql": "dbbackup.db.postgresql.PgDumpConnector",
}

if _settings.get("backup.storage.type", "").lower() == "s3":
    DBBACKUP_STORAGE = "storages.backends.s3.S3Storage"

    DBBACKUP_STORAGE_OPTIONS = {
        key: value for (key, value) in _settings.get("backup.storage.s3").items()
    }

IMPERSONATE = {"REQUIRE_SUPERUSER": True, "ALLOW_SUPERUSER": True, "REDIRECT_FIELD_NAME": "next"}

DJANGO_TABLES2_TEMPLATE = "django_tables2/materialize.html"

ANONYMIZE_ENABLED = _settings.get("maintenance.anonymisable", True)

LOGIN_URL = "login"

if _settings.get("twilio.sid", None):
    TWILIO_ACCOUNT_SID = _settings.get("twilio.sid")
    TWILIO_AUTH_TOKEN = _settings.get("twilio.token")
    TWILIO_CALLER_ID = _settings.get("twilio.callerid")

CELERY_BROKER_URL = _settings.get("celery.broker", VALKEY_URL)
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "django-cache"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_RESULT_EXTENDED = True

if _settings.get("celery.email", False):
    EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"

if _settings.get("dev.uwsgi.celery", DEBUG):
    concurrency = _settings.get("celery.uwsgi.concurrency", 2)
    UWSGI.setdefault("attach-daemon", [])
    UWSGI["attach-daemon"].append(f"celery -A aleksis.core worker --concurrency={concurrency}")
    UWSGI["attach-daemon"].append("celery -A aleksis.core beat")
    UWSGI["attach-daemon"].append("aleksis-admin vite --no-install serve")

DEFAULT_FAVICON_PATHS = {
    "pwa_icon": os.path.join(STATIC_ROOT, "img/aleksis-icon-maskable.png"),
    "favicon": os.path.join(STATIC_ROOT, "img/aleksis-favicon.png"),
}
PWA_ICONS_CONFIG = {
    "android": [192, 512],
    "apple": [76, 114, 152, 180],
    "apple_splash": [192],
    "microsoft": [144],
}
FAVICON_PATH = os.path.join("public", "favicon")
FAVICON_CONFIG = {
    "shortcut icon": [16, 32, 48, 128, 192],
    "touch-icon": [196],
    "icon": [196],
}

SERVICE_WORKER_PATH = os.path.join(STATIC_ROOT, "sw.js")

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar_Basic": [["Source", "-", "Bold", "Italic"]],
        "toolbar_Full": [
            {
                "name": "document",
                "items": ["Source", "-", "Save", "NewPage", "Preview", "Print", "-", "Templates"],
            },
            {
                "name": "clipboard",
                "items": [
                    "Cut",
                    "Copy",
                    "Paste",
                    "PasteText",
                    "PasteFromWord",
                    "-",
                    "Undo",
                    "Redo",
                ],
            },
            {"name": "editing", "items": ["Find", "Replace", "-", "SelectAll"]},
            {
                "name": "insert",
                "items": [
                    "Image",
                    "Table",
                    "HorizontalRule",
                    "Smiley",
                    "SpecialChar",
                    "PageBreak",
                    "Iframe",
                ],
            },
            "/",
            {
                "name": "basicstyles",
                "items": [
                    "Bold",
                    "Italic",
                    "Underline",
                    "Strike",
                    "Subscript",
                    "Superscript",
                    "-",
                    "RemoveFormat",
                ],
            },
            {
                "name": "paragraph",
                "items": [
                    "NumberedList",
                    "BulletedList",
                    "-",
                    "Outdent",
                    "Indent",
                    "-",
                    "Blockquote",
                    "CreateDiv",
                    "-",
                    "JustifyLeft",
                    "JustifyCenter",
                    "JustifyRight",
                    "JustifyBlock",
                    "-",
                    "BidiLtr",
                    "BidiRtl",
                    "Language",
                ],
            },
            {"name": "links", "items": ["Link", "Unlink", "Anchor"]},
            "/",
            {"name": "styles", "items": ["Styles", "Format", "Font", "FontSize"]},
            {"name": "colors", "items": ["TextColor", "BGColor"]},
            {"name": "tools", "items": ["Maximize", "ShowBlocks"]},
            {"name": "about", "items": ["About"]},
            {
                "name": "customtools",
                "items": [
                    "Preview",
                    "Maximize",
                ],
            },
        ],
        "toolbar": "Full",
        "tabSpaces": 4,
        "extraPlugins": ",".join(
            [
                "uploadimage",
                "div",
                "autolink",
                "autoembed",
                "embedsemantic",
                "autogrow",
                # 'devtools',
                "widget",
                "lineutils",
                "clipboard",
                "dialog",
                "dialogui",
                "elementspath",
            ]
        ),
    }
}

# Upload path for CKEditor. Relative to MEDIA_ROOT.
CKEDITOR_UPLOAD_PATH = "ckeditor_uploads/"

# Which HTML tags are allowed
BLEACH_ALLOWED_TAGS = ["p", "b", "i", "u", "em", "strong", "a", "div"]

# Which HTML attributes are allowed
BLEACH_ALLOWED_ATTRIBUTES = ["href", "title", "style"]

# Which CSS properties are allowed in 'style' attributes (assuming
# style is an allowed attribute)
BLEACH_ALLOWED_STYLES = ["font-family", "font-weight", "text-decoration", "font-variant"]

# Strip unknown tags if True, replace with HTML escaped characters if
# False
BLEACH_STRIP_TAGS = True

# Strip comments, or leave them in.
BLEACH_STRIP_COMMENTS = True

LOGGING = deepcopy(DEFAULT_LOGGING)
# Set root logging level as default
LOGGING["root"] = {
    "handlers": ["console"],
    "level": _settings.get("logging.level", "WARNING"),
}
# Configure global log Format
LOGGING["formatters"]["verbose"] = {
    "format": "{asctime} {levelname} {name}[{process}]: {message}",
    "style": "{",
}
# Add null handler for selective silencing
LOGGING["handlers"]["null"] = {"class": "logging.NullHandler"}
# Make console logging independent of DEBUG
LOGGING["handlers"]["console"]["filters"].remove("require_debug_true")
# Use root log level for console
del LOGGING["handlers"]["console"]["level"]
# Use verbose log format for console
LOGGING["handlers"]["console"]["formatter"] = "verbose"
# Disable exception mails if not desired
if not _settings.get("logging.mail_admins", True):
    LOGGING["loggers"]["django"]["handlers"].remove("mail_admins")
# Disable mails on disaalowed host by default
if not _settings.get("logging.disallowed_host", False):
    LOGGING["loggers"]["django.security.DisallowedHost"] = {
        "handlers": ["null"],
        "propagate": False,
    }
# Configure logging explicitly for Celery
LOGGING["loggers"]["celery"] = {
    "handlers": ["console"],
    "level": _settings.get("logging.level", "WARNING"),
    "propagate": False,
}
# Set Django log levels
LOGGING["loggers"]["django"]["level"] = _settings.get("logging.level", "WARNING")
LOGGING["loggers"]["django.server"]["level"] = _settings.get("logging.level", "WARNING")

# Rules and permissions

GUARDIAN_RAISE_403 = True
ANONYMOUS_USER_NAME = None

SILENCED_SYSTEM_CHECKS.append("guardian.W001")

# Append authentication backends
AUTHENTICATION_BACKENDS.append("rules.permissions.ObjectPermissionBackend")

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack_redis.RedisEngine",
        "PATH": VALKEY_URL,
    },
}

HAYSTACK_SIGNAL_PROCESSOR = "celery_haystack.signals.CelerySignalProcessor"
CELERY_HAYSTACK_IGNORE_RESULT = True

HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10

DJANGO_EASY_AUDIT_WATCH_REQUEST_EVENTS = False

HEALTH_CHECK = {
    "DISK_USAGE_MAX": _settings.get("health.disk_usage_max_percent", 90),
    "MEMORY_MIN": _settings.get("health.memory_min_mb", 500),
}

DBBACKUP_CHECK_SECONDS = _settings.get("backup.database.check_seconds", 7200)
MEDIABACKUP_CHECK_SECONDS = _settings.get("backup.media.check_seconds", 7200)

PROMETHEUS_EXPORT_MIGRATIONS = False
PROMETHEUS_METRICS_EXPORT_PORT = _settings.get("prometheus.metrics.port", None)
PROMETHEUS_METRICS_EXPORT_ADDRESS = _settings.get("prometheus.metrucs.address", None)

SECURE_PROXY_SSL_HEADER = ("REQUEST_SCHEME", "https")

FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

STORAGES = {
    "default": {"BACKEND": "titofisto.TitofistoStorage", "OPTIONS": {}},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        "OPTIONS": {},
    },
}


if _settings.get("storage.type", "").lower() == "s3":
    INSTALLED_APPS.append("storages")

    STORAGES["default"]["BACKEND"] = "storages.backends.s3.S3Storage"
    FILE_UPLOAD_HANDLERS.remove("django.core.files.uploadhandler.MemoryFileUploadHandler")

    if _settings.get("storage.s3.static.enabled", False):
        STORAGES["staticfiles"]["BACKEND"] = "storages.backends.s3.S3StaticStorage"
        # AWS_S3_MAX_AGE_SECONDS_CACHED_STATIC = _settings.get(
        #     "storage.s3.static.max_age_seconds", 24 * 60 * 60
        # )
        STORAGES["default"]["OPTIONS"] = {
            "region_name": _settings.get("storage.s3.static.region_name", ""),
            "access_key": _settings.get("storage.s3.static.access_key", ""),
            "secret_key": _settings.get("storage.s3.static.secret_key", ""),
            "security_token": _settings.get("storage.s3.static.session_token", ""),
            "bucket_name": _settings.get("storage.s3.static.bucket_name", ""),
            "location": _settings.get("storage.s3.static.location", ""),
            "addressing_style": _settings.get("storage.s3.static.addressing_style", "auto"),
            "endpoint_url": _settings.get("storage.s3.static.endpoint_url", ""),
            "gzip": _settings.get("storage.s3.static.gzip", True),
            "signature_version": _settings.get("storage.s3.static.signature_version", None),
            "file_overwrite": _settings.get("storage.s3.static.file_overwrite", False),
            "verify": _settings.get("storage.s3.static.verify", True),
            "use_ssl": _settings.get("storage.s3.static.use_ssl", True),
        }

    STORAGES["default"]["OPTIONS"] = {
        "region_name": _settings.get("storage.s3.region_name", ""),
        "access_key": _settings.get("storage.s3.access_key", ""),
        "secret_key": _settings.get("storage.s3.secret_key", ""),
        "security_token": _settings.get("storage.s3.session_token", ""),
        "bucket_name": _settings.get("storage.s3.bucket_name", ""),
        "location": _settings.get("storage.s3.location", ""),
        "addressing_style": _settings.get("storage.s3.addressing_style", "auto"),
        "endpoint_url": _settings.get("storage.s3.endpoint_url", ""),
        "gzip": _settings.get("storage.s3.gzip", True),
        "signature_version": _settings.get("storage.s3.signature_version", None),
        "file_overwrite": _settings.get("storage.s3.file_overwrite", False),
        "verify": _settings.get("storage.s3.verify", True),
        "use_ssl": _settings.get("storage.s3.use_ssl", True),
    }
    # AWS_S3_MAX_AGE_SECONDS = _settings.get("storage.s3.max_age_seconds", 24 * 60 * 60)
    # AWS_S3_PUBLIC_URL = _settings.get("storage.s3.public_url", "")
    # AWS_S3_REDUCED_REDUNDANCY = _settings.get("storage.s3.reduced_redundancy", False)
    # AWS_S3_CONTENT_DISPOSITION = _settings.get("storage.s3.content_disposition", "")
    # AWS_S3_CONTENT_LANGUAGE = _settings.get("storage.s3.content_language", "")
    # AWS_S3_METADATA = _settings.get("storage.s3.metadata", {})
    # AWS_S3_ENCRYPT_KEY = _settings.get("storage.s3.encrypt_key", False)
    # AWS_S3_KMS_ENCRYPTION_KEY_ID = _settings.get("storage.s3.kms_encryption_key_id", "")

TITOFISTO_TIMEOUT = 10 * 60
TITOFISTO_ENABLE_UPLOAD = True
TITOFISTO_UPLOAD_NAMESPACE = "__titofisto__/upload/"

SENTRY_ENABLED = _settings.get("health.sentry.enabled", False)
if SENTRY_ENABLED:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    SENTRY_SETTINGS = {
        "dsn": _settings.get("health.sentry.dsn"),
        "environment": _settings.get("health.sentry.environment"),
        "traces_sample_rate": _settings.get("health.sentry.traces_sample_rate", 1.0),
        "profiles_sample_rate": _settings.get("health.sentry.profiles_sample_rate", 0.0),
        "send_default_pii": _settings.get("health.sentry.send_default_pii", False),
        "in_app_include": "aleksis",
    }
    sentry_sdk.init(
        integrations=[
            DjangoIntegration(transaction_style="function_name"),
            RedisIntegration(),
            CeleryIntegration(),
        ],
        **SENTRY_SETTINGS,
    )

SHELL_PLUS_MODEL_IMPORTS_RESOLVER = "django_extensions.collision_resolvers.AppLabelPrefixCR"
SHELL_PLUS_APP_PREFIXES = {
    "auth": "auth",
}
SHELL_PLUS_DONT_LOAD = []
merge_app_settings("SHELL_PLUS_APP_PREFIXES", SHELL_PLUS_APP_PREFIXES)
merge_app_settings("SHELL_PLUS_DONT_LOAD", SHELL_PLUS_DONT_LOAD)

X_FRAME_OPTIONS = "SAMEORIGIN"

# Add django-cleanup after all apps to ensure that it gets all signals as last app
INSTALLED_APPS.append("django_cleanup.apps.CleanupConfig")

locals().update(get_app_settings_overrides())

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: f"/admin/auth/user/{o.pk}/change",
}

SELENIUM_URL = _settings.get("selenium.url", None)
