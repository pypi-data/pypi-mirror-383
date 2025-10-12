from django.db.models import PositiveSmallIntegerField

from calendarweek.django import i18n_day_name_choices_lazy


class WeekdayField(PositiveSmallIntegerField):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = i18n_day_name_choices_lazy()
        super().__init__(*args, **kwargs)
