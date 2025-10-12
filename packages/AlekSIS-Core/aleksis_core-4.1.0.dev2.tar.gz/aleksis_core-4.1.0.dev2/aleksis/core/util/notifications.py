"""Utility code for notification system."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Union

from django.apps import apps
from django.conf import settings
from django.template.loader import get_template
from django.utils import timezone
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

from .core_helpers import lazy_preference
from .email import send_email

try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    TwilioClient = None

if TYPE_CHECKING:
    from ..models import Notification


def send_templated_sms(
    template_name: str, from_number: str, recipient_list: Sequence[str], context: dict
) -> None:
    """Render a plain-text template and send via SMS to all recipients."""
    template = get_template(template_name)
    text = template.render(context)

    client = TwilioClient(settings.TWILIO_SID, settings.TWILIO_TOKEN)
    for recipient in recipient_list:
        client.messages.create(body=text, to=recipient, from_=from_number)


def _send_notification_email(notification: "Notification", template: str = "notification") -> None:
    context = {
        "notification": notification,
        "notification_user": notification.recipient.addressing_name,
    }
    send_email(
        template_name=template,
        recipient_list=[notification.recipient.email],
        context=context,
    )


def _send_notification_sms(
    notification: "Notification", template: str = "sms/notification.txt"
) -> None:
    context = {
        "notification": notification,
        "notification_user": notification.recipient.addressing_name,
    }
    send_templated_sms(
        template_name=template,
        from_number=settings.TWILIO_CALLER_ID,
        recipient_list=[notification.recipient.mobile_number.as_e164],
        context=context,
    )


# Mapping of channel id to name and two functions:
# - Check for availability
# - Send notification through it
_CHANNELS_MAP = {
    "email": (_("E-Mail"), lambda: lazy_preference("mail", "address"), _send_notification_email),
    "sms": (_("SMS"), lambda: getattr(settings, "TWILIO_SID", None), _send_notification_sms),
}


def send_notification(notification: Union[int, "Notification"], resend: bool = False) -> None:
    """Send a notification through enabled channels.

    If resend is passed as True, the notification is sent even if it was
    previously marked as sent.
    """
    if isinstance(notification, int):
        Notification = apps.get_model("core", "Notification")
        notification = Notification.objects.get(pk=notification)

    channels = [notification.recipient.preferences["notification__channels"]]

    if resend or not notification.sent:
        for channel in channels:
            name, check, send = _CHANNELS_MAP[channel]
            if check():
                send(notification)
                notification.sent = True
                notification.save()


def get_notification_choices() -> list:
    """Return all available channels for notifications.

    This gathers the channels that are technically available as per the
    system configuration. Which ones are available to users is defined
    by the administrator (by selecting a subset of these choices).
    """
    choices = []
    for channel, (name, check, send) in _CHANNELS_MAP.items():  # noqa: B007
        if check():
            choices.append((channel, name))
    return choices


get_notification_choices_lazy = lazy(get_notification_choices, tuple)


def _send_due_notifications():
    """Send all notifications that are due to be sent."""
    Notification = apps.get_model("core", "Notification")

    due_notifications = Notification.objects.filter(sent=False, send_at__lte=timezone.now())
    for notification in due_notifications:
        notification.send()
