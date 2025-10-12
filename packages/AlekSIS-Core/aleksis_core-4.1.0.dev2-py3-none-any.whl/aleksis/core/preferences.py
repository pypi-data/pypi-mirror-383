from django.conf import settings
from django.forms import EmailField, ImageField, URLField
from django.forms.widgets import SelectMultiple
from django.utils.translation import gettext_lazy as _

from colorfield.widgets import ColorWidget
from dynamic_preferences.preferences import Section
from dynamic_preferences.types import (
    BooleanPreference,
    ChoicePreference,
    FilePreference,
    IntegerPreference,
    LongStringPreference,
    ModelChoicePreference,
    ModelMultipleChoicePreference,
    MultipleChoicePreference,
    StringPreference,
)
from oauth2_provider.models import AbstractApplication

from .mixins import CalendarEventMixin, PublicFilePreferenceMixin
from .models import Address, Group, Person, Role
from .registries import person_preferences_registry, site_preferences_registry
from .util.notifications import get_notification_choices_lazy

general = Section("general", verbose_name=_("General"))
school = Section("school", verbose_name=_("School"))
theme = Section("theme", verbose_name=_("Theme"))
mail = Section("mail", verbose_name=_("Mail"))
notification = Section("notification", verbose_name=_("Notifications"))
footer = Section("footer", verbose_name=_("Footer"))
account = Section("account", verbose_name=_("Accounts"))
auth = Section("auth", verbose_name=_("Authentication"))
internationalisation = Section("internationalisation", verbose_name=_("Internationalisation"))
calendar = Section("calendar", verbose_name=_("Calendar"))
people = Section("people", verbose_name=_("People"))


@site_preferences_registry.register
class SiteTitle(StringPreference):
    """Title of the AlekSIS instance, e.g. schools display name."""

    section = general
    name = "title"
    default = "AlekSIS"
    verbose_name = _("Site title")
    required = True


@site_preferences_registry.register
class SiteDescription(StringPreference):
    """Site description, e.g. a slogan."""

    section = general
    name = "description"
    default = "The Free School Information System"
    required = False
    verbose_name = _("Site description")


@site_preferences_registry.register
class ColourPrimary(StringPreference):
    """Primary colour in AlekSIS frontend."""

    section = theme
    name = "primary"
    default = "#0d5eaf"
    verbose_name = _("Primary colour")
    widget = ColorWidget
    required = True


@site_preferences_registry.register
class ColourSecondary(StringPreference):
    """Secondary colour in AlekSIS frontend."""

    section = theme
    name = "secondary"
    default = "#0d5eaf"
    verbose_name = _("Secondary colour")
    widget = ColorWidget
    required = True


@site_preferences_registry.register
class Logo(PublicFilePreferenceMixin, FilePreference):
    """Logo of your AlekSIS instance."""

    section = theme
    field_class = ImageField
    name = "logo"
    verbose_name = _("Logo")
    required = False


@site_preferences_registry.register
class Favicon(PublicFilePreferenceMixin, FilePreference):
    """Favicon of your AlekSIS instance."""

    section = theme
    field_class = ImageField
    name = "favicon"
    verbose_name = _("Favicon")
    required = False


@site_preferences_registry.register
class PWAIcon(PublicFilePreferenceMixin, FilePreference):
    """PWA-Icon of your AlekSIS instance."""

    section = theme
    field_class = ImageField
    name = "pwa_icon"
    verbose_name = _("PWA-Icon")
    required = False


@site_preferences_registry.register
class PWAIconMaskable(BooleanPreference):
    """PWA icon is maskable."""

    section = theme
    name = "pwa_icon_maskable"
    verbose_name = _("PWA-Icon is maskable")
    default = True
    required = False


@site_preferences_registry.register
class MailOutName(StringPreference):
    """Mail out name of your AlekSIS instance."""

    section = mail
    name = "name"
    default = "AlekSIS"
    verbose_name = _("Mail out name")
    required = True


@site_preferences_registry.register
class MailOut(StringPreference):
    """Mail out address of your AlekSIS instance."""

    section = mail
    name = "address"
    default = settings.DEFAULT_FROM_EMAIL
    verbose_name = _("Mail out address")
    field_class = EmailField
    required = True


@site_preferences_registry.register
class PrivacyURL(StringPreference):
    """Link to privacy policy of your AlekSIS instance."""

    section = footer
    name = "privacy_url"
    default = ""
    required = False
    verbose_name = _("Link to privacy policy")
    field_class = URLField


@site_preferences_registry.register
class ImprintURL(StringPreference):
    """Link to imprint of your AlekSIS instance."""

    section = footer
    name = "imprint_url"
    default = ""
    required = False
    verbose_name = _("Link to imprint")
    field_class = URLField


@person_preferences_registry.register
class AddressingNameFormat(ChoicePreference):
    """User preference for addressing name format."""

    section = notification
    name = "addressing_name_format"
    default = "first_last"
    verbose_name = _("Name format for addressing")
    choices = (
        ("first_last", "John Doe"),
        ("last_fist", "Doe, John"),
    )
    required = True


@person_preferences_registry.register
class NotificationChannels(ChoicePreference):
    """User preference for notification channels."""

    # FIXME should be a MultipleChoicePreference
    section = notification
    name = "channels"
    default = "email"
    required = False
    verbose_name = _("Channels to use for notifications")
    choices = get_notification_choices_lazy()


@person_preferences_registry.register
class Design(ChoicePreference):
    """Change design (on supported pages)."""

    section = theme
    name = "design"
    default = "light"
    verbose_name = _("Select Design")
    choices = [
        ("system", _("System Design")),
        ("light", _("Light mode")),
        ("dark", _("Dark mode")),
    ]


@site_preferences_registry.register
class PrimaryGroupPattern(StringPreference):
    """Regular expression to match primary group."""

    section = account
    name = "primary_group_pattern"
    default = ""
    required = False
    verbose_name = _("Regular expression to match primary group, e.g. '^Class .*'")


@site_preferences_registry.register
class PrimaryGroupField(ChoicePreference):
    """Field on person to match primary group against."""

    section = account
    name = "primary_group_field"
    default = "name"
    required = False
    verbose_name = _("Field on person to match primary group against")

    def get_choices(self):
        return Person.syncable_fields_choices()


@site_preferences_registry.register
class AutoCreatePerson(BooleanPreference):
    section = account
    name = "auto_create_person"
    default = False
    required = False
    verbose_name = _("Automatically create new persons for new users")


@site_preferences_registry.register
class AutoLinkPerson(BooleanPreference):
    section = account
    name = "auto_link_person"
    default = False
    required = False
    verbose_name = _("Automatically link existing persons to new users by their e-mail address")


@site_preferences_registry.register
class SchoolName(StringPreference):
    """Display name of the school."""

    section = school
    name = "name"
    default = ""
    required = False
    verbose_name = _("Display name of the school")


@site_preferences_registry.register
class SchoolNameOfficial(StringPreference):
    """Official name of the school, e.g. as given by supervisory authority."""

    section = school
    name = "name_official"
    default = ""
    required = False
    verbose_name = _("Official name of the school, e.g. as given by supervisory authority")


@site_preferences_registry.register
class AllowPasswordChange(BooleanPreference):
    section = auth
    name = "allow_password_change"
    default = True
    verbose_name = _("Allow users to change their passwords")


@site_preferences_registry.register
class AllowPasswordReset(BooleanPreference):
    section = auth
    name = "allow_password_reset"
    default = True
    verbose_name = _("Allow users to reset their passwords")


@site_preferences_registry.register
class SignupEnabled(BooleanPreference):
    section = auth
    name = "signup_enabled"
    default = False
    verbose_name = _("Enable signup")


@site_preferences_registry.register
class SignupRequiredFields(MultipleChoicePreference):
    """Required fields on the person model for sign-up."""

    section = auth
    name = "signup_required_fields"
    default = []
    widget = SelectMultiple
    verbose_name = _(
        "Required fields on the person model for sign-up. First and last name are always required."
    )
    field_attribute = {"initial": []}
    choices = [
        (field.name, field.name)
        for field in Person.syncable_fields()
        if getattr(field, "blank", False)
    ]
    required = False


@site_preferences_registry.register
class SignupAddressRequiredFields(MultipleChoicePreference):
    """Required fields on the address model for sign-up."""

    section = auth
    name = "signup_address_required_fields"
    default = []
    widget = SelectMultiple
    verbose_name = _("Required fields on the address model for sign-up.")
    field_attribute = {"initial": []}
    choices = [
        (field.name, field.name)
        for field in Address.syncable_fields()
        if getattr(field, "blank", False)
    ]
    required = False


@site_preferences_registry.register
class SignupVisibleFields(MultipleChoicePreference):
    """Visible fields on the person model for sign-up."""

    section = auth
    name = "signup_visible_fields"
    default = []
    widget = SelectMultiple
    verbose_name = _(
        "Visible fields on the person model for sign-up. First and last name are always visible."
    )
    field_attribute = {"initial": []}
    choices = [
        (field.name, field.name)
        for field in Person.syncable_fields()
        if getattr(field, "blank", False)
    ]
    required = False


@site_preferences_registry.register
class SignupAddressVisibleFields(MultipleChoicePreference):
    """Visible fields on the address model for sign-up."""

    section = auth
    name = "signup_address_visible_fields"
    default = []
    widget = SelectMultiple
    verbose_name = _("Visible fields on the address model for sign-up.")
    field_attribute = {"initial": []}
    choices = [
        (field.name, field.name)
        for field in Address.syncable_fields()
        if getattr(field, "blank", False)
    ]
    required = False


@site_preferences_registry.register
class AllowedUsernameRegex(StringPreference):
    section = auth
    name = "allowed_username_regex"
    default = ".+"
    verbose_name = _("Regular expression for allowed usernames")


@site_preferences_registry.register
class InviteEnabled(BooleanPreference):
    section = auth
    name = "invite_enabled"
    default = False
    verbose_name = _("Enable invitations")


@site_preferences_registry.register
class InviteCodeLength(IntegerPreference):
    section = auth
    name = "invite_code_length"
    default = 3
    verbose_name = _("Length of invite code. (Default 3: abcde-acbde-abcde)")


@site_preferences_registry.register
class InviteCodePacketSize(IntegerPreference):
    section = auth
    name = "invite_code_packet_size"
    default = 5
    verbose_name = _("Size of packets. (Default 5: abcde)")


@site_preferences_registry.register
class OAuthAllowedGrants(MultipleChoicePreference):
    """Grant Flows allowed for OAuth applications."""

    section = auth
    name = "oauth_allowed_grants"
    default = [grant[0] for grant in AbstractApplication.GRANT_TYPES]
    widget = SelectMultiple
    verbose_name = _("Allowed Grant Flows for OAuth applications")
    field_attribute = {"initial": []}
    choices = AbstractApplication.GRANT_TYPES
    required = False


@site_preferences_registry.register
class DataChecksSendEmails(BooleanPreference):
    """Enable email sending if data checks detect problems."""

    section = general
    name = "data_checks_send_emails"
    default = False
    verbose_name = _("Send emails if data checks detect problems")


@site_preferences_registry.register
class DataChecksEmailsRecipients(ModelMultipleChoicePreference):
    """Email recipients for data check problem emails."""

    section = general
    name = "data_checks_recipients"
    default = []
    model = Person
    verbose_name = _("Email recipients for data checks problem emails")


@site_preferences_registry.register
class DataChecksEmailsRecipientGroups(ModelMultipleChoicePreference):
    """Email recipient groups for data check problem emails."""

    section = general
    name = "data_checks_recipient_groups"
    default = []
    model = Group
    verbose_name = _("Email recipient groups for data checks problem emails")


@site_preferences_registry.register
class AnonymousDashboard(BooleanPreference):
    section = general
    name = "anonymous_dashboard"
    default = False
    required = False
    verbose_name = _("Show dashboard to users without login")


@site_preferences_registry.register
class DashboardEditing(BooleanPreference):
    section = general
    name = "dashboard_editing"
    default = True
    required = False
    verbose_name = _("Allow users to edit their dashboard")


@site_preferences_registry.register
class EditableFieldsPerson(MultipleChoicePreference):
    """Fields on person model that should be editable by the person."""

    section = account
    name = "editable_fields_person"
    default = []
    widget = SelectMultiple
    verbose_name = _("Fields on person model which are editable by themselves.")
    field_attribute = {"initial": []}
    choices = [(field.name, field.name) for field in Person.syncable_fields()]
    required = False


@site_preferences_registry.register
class SendNotificationOnPersonChange(MultipleChoicePreference):
    """Fields on the person model that should trigger a notification on change."""

    section = account
    name = "notification_on_person_change"
    default = []
    widget = SelectMultiple
    verbose_name = _(
        "Editable fields on person model which should trigger a notification on change"
    )
    field_attribute = {"initial": []}
    choices = [(field.name, field.name) for field in Person.syncable_fields()]
    required = False


@site_preferences_registry.register
class PersonChangeNotificationContact(StringPreference):
    """Mail recipient address for change notifications."""

    section = account
    name = "person_change_notification_contact"
    default = ""
    verbose_name = _("Contact for notification if a person changes their data")
    required = False


@site_preferences_registry.register
class PersonAccountRegistrationContact(StringPreference):
    """Mail recipient address for account registration notifications."""

    section = account
    name = "registration_notification_contact"
    default = ""
    verbose_name = _("Contact for notification when a new account is registered")
    required = False


@site_preferences_registry.register
class PersonPreferPhoto(BooleanPreference):
    """Preference, whether personal photos should be displayed instead of avatars."""

    section = account
    name = "person_prefer_photo"
    default = False
    verbose_name = _("Prefer personal photos over avatars")


@site_preferences_registry.register
class PDFFileExpirationDuration(IntegerPreference):
    """PDF file expiration duration."""

    section = general
    name = "pdf_expiration"
    default = 3
    verbose_name = _("PDF file expiration duration")
    help_text = _("in minutes")


@person_preferences_registry.register
class AutoUpdatingDashboard(BooleanPreference):
    """User preference for automatically updating the dashboard."""

    section = general
    name = "automatically_update_dashboard"
    default = True
    verbose_name = _("Automatically update the dashboard and its widgets")


@site_preferences_registry.register
class AutoUpdatingDashboardSite(BooleanPreference):
    """Automatic updating of dashboard."""

    section = general
    name = "automatically_update_dashboard_site"
    default = True
    verbose_name = _("Automatically update the dashboard and its widgets sitewide")


@site_preferences_registry.register
class FirstDayOfTheWeekSite(ChoicePreference):
    """First Day that appears in the calendar."""

    section = calendar
    name = "first_day_of_the_week"
    default = "1"
    verbose_name = _("First day that appears in the calendar")
    choices = (
        ("1", _("Monday")),
        ("2", _("Tuesday")),
        ("3", _("Wednesday")),
        ("4", _("Thursday")),
        ("5", _("Friday")),
        ("6", _("Saturday")),
        ("0", _("Sunday")),
    )
    required = False


@person_preferences_registry.register
class FirstDayOfTheWeekPerson(ChoicePreference):
    """First Day that appears in the calendar.
    Defaults to the site preference
    """

    section = calendar
    name = "first_day_of_the_week"
    default = "default"
    verbose_name = _("First day that appears in the calendar")
    choices = (
        ("default", _("Use page default")),
        ("1", _("Monday")),
        ("2", _("Tuesday")),
        ("3", _("Wednesday")),
        ("4", _("Thursday")),
        ("5", _("Friday")),
        ("6", _("Saturday")),
        ("0", _("Sunday")),
    )
    required = True


@site_preferences_registry.register
class BirthdayFeedColor(StringPreference):
    """Color for the birthdays calendar feed."""

    section = calendar
    name = "birthday_color"
    default = "#f39c12"
    verbose_name = _("Birthday calendar feed color")
    widget = ColorWidget
    required = True


@site_preferences_registry.register
class HolidayFeedColor(StringPreference):
    """Color for the holidays calendar feed."""

    section = calendar
    name = "holiday_color"
    default = "#00b894"
    verbose_name = _("Holiday calendar feed color")
    widget = ColorWidget
    required = True


@site_preferences_registry.register
class AvailabilityEventFeedColor(StringPreference):
    """Color for the availability event calendar feed."""

    section = calendar
    name = "availability_event_feed_color"
    default = "#0d5eaf"
    verbose_name = _("Free/busy event calendar feed color")
    widget = ColorWidget
    required = True


@site_preferences_registry.register
class AvailabilityEventFreeColor(StringPreference):
    """Color of free events in the availability event calendar feed."""

    section = calendar
    name = "availability_event_free_color"
    default = "#4caf50"
    verbose_name = _("Color of free events in availability event calendar feed")
    widget = ColorWidget
    required = True


@site_preferences_registry.register
class AvailabilityEventBusyColor(StringPreference):
    """Color of busy events in the availability event calendar feed."""

    section = calendar
    name = "availability_event_busy_color"
    default = "#f44336"
    verbose_name = _("Color of busy events in availability event calendar feed")


@site_preferences_registry.register
class FreeBusyFreeColor(StringPreference):
    """Color of free time spans in the aggregated free/busy calendar feed."""

    section = calendar
    name = "freebusy_free_color"
    default = "#4caf50"
    verbose_name = _("Color of free events in aggregated free/busy calendar feed.")
    widget = ColorWidget
    required = True


@site_preferences_registry.register
class FreeBusyBusyColor(StringPreference):
    """Color of busy time spans in the aggregated free/busy calendar feed."""

    section = calendar
    name = "freebusy_busy_color"
    default = "#f44336"
    verbose_name = _("Color of busy events in aggregated free/busy calendar feed.")


@site_preferences_registry.register
class PersonalEventFeedColor(StringPreference):
    """Color for the personal events calendar feed."""

    section = calendar
    name = "personal_event_color"
    default = "#0d5eaf"
    verbose_name = _("Personal events feed color")
    widget = ColorWidget
    required = True


@person_preferences_registry.register
class ActivatedCalendars(MultipleChoicePreference):
    """Calendars that are activated for a person."""

    section = calendar
    name = "activated_calendars"
    default = []
    widget = SelectMultiple
    verbose_name = _("Activated calendars")
    required = False

    field_attribute = {"initial": []}
    choices = [(feed._class_name, feed.dav_verbose_name) for feed in CalendarEventMixin.valid_feeds]


@site_preferences_registry.register
class DisallowedUids(LongStringPreference):
    section = auth
    name = "disallowed_uids"
    default = (
        "bin,daemon,Debian-exim,freerad,games,gnats,irc,list,lp,mail,man,messagebus,news,"
        "nslcd,ntp,openldap,postfix,postgres,proxy,root,sshd,sssd,statd,sync,sys,systemd-bus-proxy,"
        "systemd-network,systemd-resolve,systemd-timesync,uucp,www-data,"
        "webmaster,hostmaster,postmaster"
    )
    required = False
    verbose_name = _("Comma-separated list of disallowed usernames")


@site_preferences_registry.register
class PersonRoles(ModelMultipleChoicePreference):
    section = people
    name = "roles"
    default = []
    model = Role
    verbose_name = _("Roles selectable for Person-to-Person relationships")


@site_preferences_registry.register
class InviterRole(ModelChoicePreference):
    """Role set for a relationship between inviter and invitee."""

    section = auth
    name = "inviter_role"
    default = None
    model = Role
    verbose_name = _("Role set for a relationship between inviter and invitee")
