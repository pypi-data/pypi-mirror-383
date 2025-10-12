from django.conf import settings
from django.utils import translation

import graphene
from maintenance_mode.core import get_maintenance_mode

from ..models import CustomMenu
from ..util.core_helpers import get_site_preferences
from ..util.frontend_helpers import get_language_cookie
from .custom_menu import CustomMenuType
from .site_preferences import SitePreferencesType


class AdminType(graphene.ObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)

    @staticmethod
    def resolve_name(root, info):
        return root[0]

    @staticmethod
    def resolve_email(root, info):
        return root[1]


class LanguageType(graphene.ObjectType):
    code = graphene.String(required=True)
    name = graphene.String(required=True)
    name_local = graphene.String(required=True)
    name_translated = graphene.String(required=True)
    bidi = graphene.Boolean(required=True)
    cookie = graphene.String(required=True)


class SystemPropertiesType(graphene.ObjectType):
    current_language = graphene.String(required=True)
    default_language = graphene.Field(LanguageType)
    available_languages = graphene.List(LanguageType)
    site_preferences = graphene.Field(SitePreferencesType)
    custom_menu_by_name = graphene.Field(CustomMenuType)

    debug_mode = graphene.Boolean()
    maintenance_mode = graphene.Boolean()

    admins = graphene.List(AdminType)

    def resolve_current_language(parent, info, **kwargs):
        return info.context.LANGUAGE_CODE

    @staticmethod
    def resolve_default_language(root, info, **kwargs):
        code = settings.LANGUAGE_CODE
        return translation.get_language_info(code) | {"cookie": get_language_cookie(code)}

    def resolve_available_languages(parent, info, **kwargs):
        return [
            translation.get_language_info(code) | {"cookie": get_language_cookie(code)}
            for code, name in settings.LANGUAGES
        ]

    def resolve_site_preferences(root, info, **kwargs):
        return get_site_preferences()

    def resolve_custom_menu_by_name(root, info, name, **kwargs):
        return CustomMenu.get_default(name)

    def resolve_debug_mode(root, info, **kwargs):
        if not info.context.user.has_perm("core.view_system_status_rule"):
            return None

        return settings.DEBUG

    def resolve_maintenance_mode(root, info, **kwargs):
        if not info.context.user.has_perm("core.view_system_status_rule"):
            return None

        return get_maintenance_mode()

    @staticmethod
    def resolve_admins(root, info, **kwargs):
        return settings.ADMINS
