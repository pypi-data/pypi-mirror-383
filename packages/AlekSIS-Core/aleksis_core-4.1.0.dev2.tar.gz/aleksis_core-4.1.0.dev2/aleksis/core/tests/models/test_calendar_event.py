from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest
from recurrence import WEEKLY, Recurrence, Rule

from aleksis.core.models import CalendarEvent, Person, PersonalEvent

pytestmark = pytest.mark.django_db


def test_calendar_event_timezone():
    datetime_start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc).astimezone(
        ZoneInfo("Europe/Berlin")
    )
    datetime_end = datetime(2024, 12, 31, 0, 0, tzinfo=timezone.utc).astimezone(
        ZoneInfo("Europe/Berlin")
    )

    # No timezone set
    calendar_event = CalendarEvent.objects.create(
        datetime_start=datetime_start, datetime_end=datetime_end
    )
    calendar_event.refresh_from_db()

    assert calendar_event.datetime_start == datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert calendar_event.datetime_end == datetime(2024, 12, 31, 0, 0, tzinfo=timezone.utc)
    assert CalendarEvent.value_start_datetime(calendar_event) == datetime(
        2024, 1, 1, 0, 0, tzinfo=timezone.utc
    )
    assert CalendarEvent.value_end_datetime(calendar_event) == datetime(
        2024, 12, 31, 0, 0, tzinfo=timezone.utc
    )
    assert calendar_event.timezone is None

    # Set timezone if not allowed
    calendar_event.timezone = ZoneInfo("Europe/Berlin")
    calendar_event.save()
    calendar_event.refresh_from_db()
    assert calendar_event.timezone is None

    # Automatically set timezone
    calendar_event.datetime_start = datetime_start
    calendar_event.datetime_end = datetime_end
    calendar_event.recurrences = Recurrence(dtstart=datetime_start, rrules=[Rule(WEEKLY)])
    calendar_event.save()
    calendar_event.refresh_from_db()

    assert calendar_event.datetime_start == datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert calendar_event.datetime_end == datetime(2024, 12, 31, 0, 0, tzinfo=timezone.utc)
    assert CalendarEvent.value_start_datetime(calendar_event) == datetime_start
    assert CalendarEvent.value_end_datetime(calendar_event) == datetime_end
    assert calendar_event.timezone == ZoneInfo("Europe/Berlin")

    # Manually set timezone (e. g. from frontend)
    calendar_event.timezone = ZoneInfo("Europe/Berlin")
    calendar_event.save()
    calendar_event.refresh_from_db()
    assert calendar_event.timezone == ZoneInfo("Europe/Berlin")


def test_calendar_event_recurring_timezones_all_objects():
    tz = ZoneInfo("Europe/Berlin")
    owner = Person.objects.create(first_name="Foo", last_name="Baz")
    start_dt = datetime(2025, 3, 26, 18, 0, tzinfo=tz)
    end_dt = datetime(2025, 3, 26, 19, 0, tzinfo=tz)
    end_rrule = datetime(2025, 4, 2, 19, 0, tzinfo=tz)

    event = PersonalEvent()
    event.datetime_start = start_dt
    event.datetime_end = end_dt
    event.recurrences = Recurrence(dtstart=start_dt, rrules=[Rule(WEEKLY, until=end_rrule)])
    event.owner = owner
    event.title = "Test Event"
    event.save()

    events = sorted(
        event.get_objects(expand=True, start=datetime(2025, 1, 1), end=datetime(2025, 12, 31)),
        key=lambda event: event.odatetime,
    )
    assert len(events) == 2
    obj1 = events[0]
    obj2 = events[1]

    assert obj1.value_start_datetime(obj1).tzinfo == tz
    assert obj1.value_start_datetime(obj1) == start_dt

    assert obj2.value_start_datetime(obj2).tzinfo == tz
    assert obj2.value_start_datetime(obj2) == datetime(2025, 4, 2, 18, 0, tzinfo=tz)


def test_calendar_event_recurring_timezones_in_range():
    tz = ZoneInfo("Europe/Berlin")
    owner = Person.objects.create(first_name="Foo", last_name="Baz")
    start_dt = datetime(2025, 3, 26, 18, 0, tzinfo=tz)
    end_dt = datetime(2025, 3, 26, 19, 0, tzinfo=tz)
    end_rrule = datetime(2025, 4, 2, 19, 0, tzinfo=tz)

    event = PersonalEvent()
    event.datetime_start = start_dt
    event.datetime_end = end_dt
    event.recurrences = Recurrence(dtstart=start_dt, rrules=[Rule(WEEKLY, until=end_rrule)])
    event.owner = owner
    event.title = "Test Event"
    event.save()

    # Exact range
    events = event.get_objects(start=start_dt, end=end_dt, expand=True)
    assert events.count() == 1
    obj1 = events[0]
    assert obj1.value_start_datetime(obj1).tzinfo == tz
    assert obj1.value_start_datetime(obj1) == start_dt

    # Exact range with second occurrence (shifted because of DST)
    events = event.get_objects(
        start=datetime(2025, 4, 2, 18, 0, tzinfo=tz),
        end=datetime(2025, 4, 2, 19, 0, tzinfo=tz),
        expand=True,
    )
    assert events.count() == 1
    obj1 = events[0]
    assert obj1.value_start_datetime(obj1).tzinfo == tz
    assert obj1.value_start_datetime(obj1) == datetime(2025, 4, 2, 18, 0, tzinfo=tz)

    # Extended range with second occurrence
    events = event.get_objects(
        start=datetime(2025, 4, 2, 17, 0, tzinfo=tz),
        end=datetime(2025, 4, 2, 20, 0, tzinfo=tz),
        expand=True,
    )
    assert events.count() == 1
    obj1 = events[0]
    assert obj1.value_start_datetime(obj1).tzinfo == tz
    assert obj1.value_start_datetime(obj1) == datetime(2025, 4, 2, 18, 0, tzinfo=tz)

    # Partial range with first occurrence
    events = event.get_objects(
        start=datetime(2025, 3, 26, 18, 0, tzinfo=tz),
        end=datetime(2025, 3, 26, 18, 30, tzinfo=tz),
        expand=True,
    )
    assert events.count() == 1
    obj1 = events[0]
    assert obj1.value_start_datetime(obj1).tzinfo == tz
    assert obj1.value_start_datetime(obj1) == start_dt

    # Partial range with second occurrence
    events = event.get_objects(
        start=datetime(2025, 4, 2, 18, 0, tzinfo=tz),
        end=datetime(2025, 4, 2, 18, 30, tzinfo=tz),
        expand=True,
    )
    assert events.count() == 1
    obj1 = events[0]
    assert obj1.value_start_datetime(obj1).tzinfo == tz
    assert obj1.value_start_datetime(obj1) == datetime(2025, 4, 2, 18, 0, tzinfo=tz)


def test_calendar_event_recurring_timezones_not_in_range():
    tz = ZoneInfo("Europe/Berlin")
    owner = Person.objects.create(first_name="Foo", last_name="Baz")
    start_dt = datetime(2025, 3, 26, 18, 0, tzinfo=tz)
    end_dt = datetime(2025, 3, 26, 19, 0, tzinfo=tz)
    end_rrule = datetime(2025, 4, 2, 19, 0, tzinfo=tz)

    event = PersonalEvent()
    event.datetime_start = start_dt
    event.datetime_end = end_dt
    event.recurrences = Recurrence(dtstart=start_dt, rrules=[Rule(WEEKLY, until=end_rrule)])
    event.owner = owner
    event.title = "Test Event"
    event.save()

    events = event.get_objects(
        start=datetime(2025, 4, 2, 19, 0, tzinfo=tz),
        end=datetime(2025, 4, 2, 20, 0, tzinfo=tz),
        expand=True,
    )
    assert events.count() == 0
