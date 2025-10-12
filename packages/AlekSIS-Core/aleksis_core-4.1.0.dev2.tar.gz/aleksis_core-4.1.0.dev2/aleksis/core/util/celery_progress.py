from collections.abc import Generator, Iterable, Sequence
from functools import wraps
from numbers import Number
from typing import Callable, Optional, Union

from django.contrib import messages

from celery_progress.backend import PROGRESS_STATE, AbstractProgressRecorder

from ..celery import app
from ..tasks import send_notification_for_done_task


class ProgressRecorder(AbstractProgressRecorder):
    """Track the progress of a Celery task and give data to the frontend.

    This recorder provides the functions `set_progress` and `add_message`
    which can be used to track the status of a Celery task.

    How to use
    ----------
    1. Write a function and include tracking methods

    ::

        from django.contrib import messages

        from aleksis.core.util.celery_progress import recorded_task

        @recorded_task
        def do_something(foo, bar, recorder, baz=None):
            # ...
            recorder.set_progress(total=len(list_with_data))

            for i, item in enumerate(list_with_data):
                # ...
                recorder.set_progress(i + 1)
                # ...

            recorder.add_message(messages.SUCCESS, "All data were imported successfully.")

    You can also use `recorder.iterate` to simplify iterating and counting.

    2. Track progress:

    ::

        # Render progress view
        do_something.delay_with_progress(foo, bar, baz=baz, TaskUserAssignment(
            user=...,
            title=_("Progress: Import data"),
            back_url=reverse("index"),
            progress_title=_("Import objects …"),
            success_message=_("The import was done successfully."),
            error_message=_("There was a problem while importing data."),
        ))

    Please take a look at the documentation of ``TaskUserAssignment``
    to get all available options.
    """

    def __init__(self, task):
        self.task = task
        self._messages = []
        self._current = 0
        self._total = 100
        self.set_progress()

    def iterate(self, data: Union[Iterable, Sequence], total: Optional[int] = None) -> Generator:
        """Iterate over a sequence or iterable, updating progress on the move.

        ::

            @recorded_task
            def do_something(long_list, recorder):
                for item in recorder.iterate(long_list):
                    do_something_with(item)

        :param data: A sequence (tuple, list, set,...) or an iterable
        :param total: Total number of items, in case data does not support len()
        """
        if total is None and hasattr(data, "__len__"):
            total = len(data)
        else:
            raise TypeError("No total value passed, and data does not support len()")

        for current, item in enumerate(data):
            self.set_progress(current, total)
            yield item

    def set_progress(
        self,
        current: Optional[Number] = None,
        total: Optional[Number] = None,
        description: Optional[str] = None,
        level: int = messages.INFO,
    ):
        """Set the current progress in the frontend.

        The progress percentage is automatically calculated in relation to self.total.

        :param current: The number of processed items; relative to total, default unchanged
        :param total: The total number of items (or 100 if using a percentage), default unchanged
        :param description: A textual description, routed to the frontend as an INFO message
        """
        if current is not None:
            self._current = current
        if total is not None:
            self._total = total

        percent = 0
        if self._total > 0:
            percent = self._current / self._total * 100

        if description is not None:
            self._messages.append((level, description))

        self.task.update_state(
            state=PROGRESS_STATE,
            meta={
                "current": self._current,
                "total": self._total,
                "percent": percent,
                "messages": self._messages,
            },
        )

    def add_message(self, level: int, message: str) -> None:
        """Show a message in the progress frontend.

        This method is a shortcut for set_progress with no new progress arguments,
        passing only the message and level as description.

        :param level: The message level (default levels from django.contrib.messages)
        :param message: The actual message (should be translated)
        """
        self.set_progress(description=message, level=level)


def recorded_task(orig: Optional[Callable] = None, **kwargs) -> Union[Callable, app.Task]:
    """Create a Celery task that receives a ProgressRecorder.

    Returns a Task object with a wrapper that passes the recorder instance
    as the recorder keyword argument.
    """

    def _real_decorator(orig: Callable) -> app.Task:
        @wraps(orig)
        def _inject_recorder(task, *args, **kwargs):
            recorder = ProgressRecorder(task)
            orig(*args, **kwargs, recorder=recorder)

            # Start notification task to ensure
            # that the user is informed about the result in any case
            send_notification_for_done_task.delay(task.request.id)

            return recorder._messages

        # Force bind to True because _inject_recorder needs the Task object
        kwargs["bind"] = True
        return app.task(_inject_recorder, **kwargs)

    if orig and not kwargs:
        return _real_decorator(orig)
    return _real_decorator
