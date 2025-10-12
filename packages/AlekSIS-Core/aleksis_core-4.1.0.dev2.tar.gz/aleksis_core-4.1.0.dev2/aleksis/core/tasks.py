import time
from datetime import timedelta

from django.conf import settings
from django.core import management

from .celery import app
from .util.notifications import _send_due_notifications as _send_due_notifications
from .util.notifications import send_notification as _send_notification


@app.task
def send_notification(notification: int, resend: bool = False) -> None:
    """Send a notification object to its recipient.

    :param notification: primary key of the notification object to send
    :param resend: Define whether to also send if the notification was already sent
    """
    _send_notification(notification, resend)


@app.task
def update_or_create_notifications_for_alarm(alarm: int) -> None:
    """Update or create notifications for a calendar alarm.

    This is done in a Celery task as it may take a while with many recipients.
    """
    from .models import CalendarAlarm

    alarm = CalendarAlarm.objects.get(pk=alarm)
    alarm._update_or_create_notifications()


@app.task(run_every=timedelta(days=1))
def backup_data() -> None:
    """Backup database and media using django-dbbackup."""
    # Assemble command-line options for dbbackup management command
    db_options = []
    if settings.DBBACKUP_COMPRESS_DB:
        db_options.append("-z")
    if settings.DBBACKUP_ENCRYPT_DB:
        db_options.append("-e")
    if settings.DBBACKUP_CLEANUP_DB:
        db_options.append("-c")

    media_options = []
    if settings.DBBACKUP_COMPRESS_MEDIA:
        media_options.append("-z")
    if settings.DBBACKUP_ENCRYPT_MEDIA:
        media_options.append("-e")
    if settings.DBBACKUP_CLEANUP_MEDIA:
        media_options.append("-c")

    # Hand off to dbbackup's management commands
    management.call_command("dbbackup", *db_options)
    management.call_command("mediabackup", *media_options)


@app.task(run_every=timedelta(days=1))
def clear_oauth_tokens():
    """Clear expired OAuth2 tokens."""
    from oauth2_provider.models import clear_expired  # noqa

    return clear_expired()


@app.task(run_every=timedelta(minutes=5))
def send_notifications():
    """Send due notifications to users."""
    _send_due_notifications()


@app.task
def send_notification_for_done_task(task_id):
    """Send a notification for a done task."""
    from aleksis.core.models import TaskUserAssignment

    # Wait five seconds to ensure that the client has received the final status
    time.sleep(5)

    try:
        assignment = TaskUserAssignment.objects.get(task_id=task_id)
    except TaskUserAssignment.DoesNotExist:
        # No foreground task
        return

    if not assignment.result_fetched:
        assignment.create_notification()
