import logging
import os
from traceback import format_exception
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aleksis.core.models import TaskUserAssignment
from django.conf import settings
from django.db import transaction

from celery import Celery
from celery.contrib.django.task import DjangoTask
from celery.signals import setup_logging, task_failure

from .util.core_helpers import get_site_preferences
from .util.email import send_email

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aleksis.core.settings")


class CeleryTask(DjangoTask):
    """Custom Task object for progress tracking."""

    def delay_with_progress(
        self, user_assignment: "TaskUserAssignment", *args, **kwargs
    ) -> "TaskUserAssignment":
        """Start task and track the progress."""
        user_assignment.save()

        def _inner():
            task_result = self.delay(*args, **kwargs)
            user_assignment.task_id = task_result.id
            user_assignment.save()

        transaction.on_commit(_inner)
        return user_assignment


app = Celery("aleksis", task_cls=CeleryTask)  # noqa
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@task_failure.connect
def task_failure_notifier(
    sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, **__
):
    recipient_list = [e[1] for e in settings.ADMINS]
    send_email(
        template_name="celery_failure",
        from_email=get_site_preferences()["mail__address"],
        recipient_list=recipient_list,
        context={
            "task_name": sender.name,
            "task": str(sender),
            "task_id": str(task_id),
            "exception": str(exception),
            "args": args,
            "kwargs": kwargs,
            "traceback": "".join(format_exception(type(exception), exception, traceback)),
        },
    )


@setup_logging.connect
def on_setup_logging(*args, **kwargs):
    """Load Django's logging configuration when running inside Celery."""
    logging.config.dictConfig(settings.LOGGING)
