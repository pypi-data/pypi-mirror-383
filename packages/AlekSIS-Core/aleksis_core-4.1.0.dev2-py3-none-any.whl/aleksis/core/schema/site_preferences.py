from django.templatetags.static import static

import graphene


class ThemeLogoType(graphene.ObjectType):
    url = graphene.String(required=False)


class SitePreferencesType(graphene.ObjectType):
    general_title = graphene.String()

    theme_logo = graphene.Field(ThemeLogoType)
    theme_primary = graphene.String()
    theme_secondary = graphene.String()
    theme_design = graphene.String()

    footer_imprint_url = graphene.String()
    footer_privacy_url = graphene.String()

    account_person_prefer_photo = graphene.Boolean()

    calendar_days_of_the_week = graphene.List(graphene.Int)

    editable_fields_person = graphene.List(graphene.String)

    invite_enabled = graphene.Boolean()
    signup_enabled = graphene.Boolean()
    signup_required_fields = graphene.List(graphene.String)
    signup_address_required_fields = graphene.List(graphene.String)
    signup_visible_fields = graphene.List(graphene.String)
    signup_address_visible_fields = graphene.List(graphene.String)

    auth_allowed_username_regex = graphene.String()
    auth_disallowed_uids = graphene.List(graphene.String)

    def resolve_general_title(parent, info, **kwargs):
        return parent["general__title"]

    def resolve_theme_logo(parent, info, **kwargs):
        return (
            parent["theme__logo"]
            if parent["theme__logo"]
            else {"url": static("/img/aleksis-banner.svg")}
        )

    def resolve_theme_primary(parent, info, **kwargs):
        return parent["theme__primary"]

    def resolve_theme_secondary(parent, info, **kwargs):
        return parent["theme__secondary"]

    def resolve_theme_design(parent, info, **kwargs):
        if info.context.user and not info.context.user.is_anonymous and info.context.user.person:
            return info.context.user.person.preferences["theme__design"]
        return "light"

    def resolve_footer_imprint_url(parent, info, **kwargs):
        return parent["footer__imprint_url"]

    def resolve_footer_privacy_url(parent, info, **kwargs):
        return parent["footer__privacy_url"]

    def resolve_account_person_prefer_photo(parent, info, **kwargs):
        return parent["account__person_prefer_photo"]

    def resolve_calendar_days_of_the_week(parent, info, **kwargs):
        first = int(parent["calendar__first_day_of_the_week"])

        if first != 0:
            return list(range(first, 7)) + list(range(0, first))
        else:
            return list(range(first, 7))

    def resolve_editable_fields_person(parent, info, **kwargs):
        return parent["account__editable_fields_person"]

    def resolve_invite_enabled(parent, info, **kwargs):
        return parent["auth__invite_enabled"]

    def resolve_auth_allowed_username_regex(parent, info, **kwargs):
        return parent["auth__allowed_username_regex"]

    def resolve_auth_disallowed_uids(parent, info, **kwargs):
        return parent["auth__disallowed_uids"].split(",")

    def resolve_signup_enabled(parent, info, **kwargs):
        return parent["auth__signup_enabled"]

    def resolve_signup_required_fields(parent, info, **kwargs):
        return parent["auth__signup_required_fields"]

    def resolve_signup_address_required_fields(parent, info, **kwargs):
        return parent["auth__signup_address_required_fields"]

    def resolve_signup_visible_fields(parent, info, **kwargs):
        return parent["auth__signup_visible_fields"]

    def resolve_signup_address_visible_fields(parent, info, **kwargs):
        return parent["auth__signup_address_visible_fields"]
