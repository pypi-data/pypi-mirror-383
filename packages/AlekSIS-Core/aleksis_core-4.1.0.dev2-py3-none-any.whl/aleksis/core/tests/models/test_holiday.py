from datetime import date, datetime

import pytest
from recurrence import WEEKLY, Recurrence, Rule

from aleksis.core.models import Holiday

pytestmark = pytest.mark.django_db


def test_holiday_get_days():
    holiday = Holiday.objects.create(
        date_start=date(2024, 2, 1), date_end=date(2024, 2, 4), holiday_name="Test Holiday"
    )
    assert set(holiday.get_days()) == {
        date(2024, 2, 1),
        date(2024, 2, 2),
        date(2024, 2, 3),
        date(2024, 2, 4),
    }


def test_holiday_exdates():
    holiday = Holiday.objects.create(
        date_start=date(2024, 2, 1), date_end=date(2024, 2, 28), holiday_name="Test Holiday"
    )

    pattern = Recurrence(datetime(2024, 2, 3))
    pattern.rrules.append(Rule(WEEKLY, until=datetime(2024, 6, 1)))

    exdates = holiday.get_ex_dates(datetime(2024, 2, 3), datetime(2024, 4, 1), pattern)
    assert set(exdates) == {
        datetime(2024, 2, 3),
        datetime(2024, 2, 10),
        datetime(2024, 2, 17),
        datetime(2024, 2, 24),
    }
