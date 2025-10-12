import json
import os
from collections.abc import Sequence
from datetime import datetime, timedelta
from importlib import import_module, metadata
from itertools import groupby
from operator import itemgetter
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Optional, Union
from warnings import warn

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files import File
from django.db.models import Model, Q, QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.functional import lazy
from django.utils.module_loading import import_string

import django_ical.feedgenerator as feedgenerator
from cache_memoize import cache_memoize
from icalendar import Calendar, Component, Event, FreeBusy, Timezone, Todo

if TYPE_CHECKING:
    from django.contrib.contenttypes.models import ContentType

    from favicon.models import Favicon


def copyright_years(years: Sequence[int], separator: str = ", ", joiner: str = "–") -> str:
    """Take a sequence of integers and produces a string with ranges.

    >>> copyright_years([1999, 2000, 2001, 2005, 2007, 2008, 2009])
    '1999–2001, 2005, 2007–2009'
    """
    ranges = [
        list(map(itemgetter(1), group))
        for _, group in groupby(enumerate(years), lambda e: e[1] - e[0])
    ]
    years_strs = [
        str(range_[0]) if len(range_) == 1 else joiner.join([str(range_[0]), str(range_[-1])])
        for range_ in ranges
    ]

    return separator.join(years_strs)


def get_app_packages(only_official: bool = False) -> Sequence[str]:
    """Find all registered apps from the setuptools entrypoint."""
    apps = []

    for ep in metadata.entry_points(group="aleksis.app"):
        path = f"{ep.module}.{ep.attr}"
        if path.startswith("aleksis.apps.") or not only_official:
            apps.append(path)

    return apps


def get_app_module(app: str, name: str) -> Optional[ModuleType]:
    """Get a named module of an app."""
    pkg = ".".join(app.split(".")[:-2])

    while "." in pkg:
        try:
            return import_module(f"{pkg}.{name}")
        except ImportError:
            # Import errors are non-fatal.
            pkg = ".".join(pkg.split(".")[:-1])

    # The app does not have this module
    return None


def merge_app_settings(
    setting: str, original: Union[dict, list], deduplicate: bool = False
) -> Union[dict, list]:
    """Merge app settings.

    Get a named settings constant from all apps and merge it into the original.
    To use this, add a settings.py file to the app, in the same format as Django's
    main settings.py.

    Note: Only selected names will be imported frm it to minimise impact of
    potentially malicious apps!
    """
    for app in get_app_packages():
        mod_settings = get_app_module(app, "settings")
        if not mod_settings:
            continue

        app_setting = getattr(mod_settings, setting, None)
        if not app_setting:
            # The app might not have this setting or it might be empty. Ignore it in that case.
            continue

        for entry in app_setting:
            if entry in original:
                if not deduplicate:
                    raise AttributeError(f"{entry} already set in original.")
            else:
                if isinstance(original, list):
                    original.append(entry)
                elif isinstance(original, dict):
                    original[entry] = app_setting[entry]
                else:
                    raise TypeError("Only dict and list settings can be merged.")


def get_app_settings_overrides() -> dict[str, Any]:
    """Get app settings overrides.

    Official apps (those under the ``aleksis.apps` namespace) can override
    or add settings by listing them in their ``settings.overrides``.
    """
    overrides = {}

    for app in get_app_packages(True):
        mod_settings = get_app_module(app, "settings")
        if not mod_settings:
            continue

        if hasattr(mod_settings, "overrides"):
            for name in mod_settings.overrides:
                overrides[name] = getattr(mod_settings, name)

    return overrides


def get_site_preferences():
    """Get the preferences manager of the current site."""
    from ..registries import site_preferences_registry  # noqa

    return site_preferences_registry.manager()


def lazy_preference(section: str, name: str) -> Callable[[str, str], Any]:
    """Lazily get a config value from dynamic preferences.

    Useful to bind preferences
    to other global settings to make them available to third-party apps that are not
    aware of dynamic preferences.
    """

    def _get_preference(section: str, name: str) -> Any:
        return get_site_preferences()[f"{section}__{name}"]

    # The type is guessed from the default value to improve lazy()'s behaviour
    # FIXME Reintroduce the behaviour described above
    return lazy(_get_preference, str)(section, name)


def get_or_create_favicon(title: str, default: str, is_favicon: bool = False) -> "Favicon":
    """Ensure that there is always a favicon object."""
    from favicon.models import Favicon  # noqa

    if not os.path.exists(default):
        warn("staticfiles are not ready yet, not creating default icons")
        return
    elif os.path.isdir(default):
        raise ImproperlyConfigured(f"staticfiles are broken: unexpected directory at {default}")

    favicon, created = Favicon.on_site.get_or_create(
        title=title, defaults={"isFavicon": is_favicon}
    )

    changed = False

    if favicon.isFavicon != is_favicon:
        favicon.isFavicon = True
        changed = True

    if created:
        with open(default, "rb") as f:
            favicon.faviconImage.save(os.path.basename(default), File(f))
        changed = True

    if changed:
        favicon.save()

    return favicon


def get_pwa_icons():
    from django.conf import settings  # noqa

    favicon = get_or_create_favicon("pwa_icon", settings.DEFAULT_FAVICON_PATHS["pwa_icon"])
    favicon_imgs = favicon.get_favicons(config_override=settings.PWA_ICONS_CONFIG)
    return favicon_imgs


def is_impersonate(request: HttpRequest) -> bool:
    """Check whether the user was impersonated by an admin."""
    if hasattr(request, "user"):
        return getattr(request.user, "is_impersonate", False)
    else:
        return False


def has_person(obj: Union[HttpRequest, Model]) -> bool:
    """Check wehether a model object has a person attribute linking it to a Person object.

    The passed object can also be a HttpRequest object, in which case its
    associated User object is unwrapped and tested.
    """
    if isinstance(obj, HttpRequest):
        if hasattr(obj, "user"):
            obj = obj.user
        else:
            return False

    if obj.is_anonymous:
        return False

    person = getattr(obj, "person", None)
    return not (person is None or getattr(person, "is_dummy", False))


def custom_information_processor(request: Union[HttpRequest, None]) -> dict:
    """Provide custom information in all templates."""
    pwa_icons = get_pwa_icons()
    regrouped_pwa_icons = {}
    for pwa_icon in pwa_icons:
        regrouped_pwa_icons.setdefault(pwa_icon.rel, {})
        regrouped_pwa_icons[pwa_icon.rel][pwa_icon.size] = pwa_icon

    # This dictionary is passed to the frontend and made available as
    #  `$root.$aleksisFrontendSettings` in Vue.
    frontend_settings = {
        "sentry": {
            "enabled": settings.SENTRY_ENABLED,
        },
        "urls": {
            "base": settings.BASE_URL,
            "graphql": reverse("graphql"),
        },
    }

    context = {
        "ADMINS": settings.ADMINS,
        "PWA_ICONS": regrouped_pwa_icons,
        "SENTRY_ENABLED": settings.SENTRY_ENABLED,
        "SITE_PREFERENCES": get_site_preferences(),
        "BASE_URL": settings.BASE_URL,
        "FRONTEND_SETTINGS": frontend_settings,
    }

    if settings.SENTRY_ENABLED:
        frontend_settings["sentry"].update(settings.SENTRY_SETTINGS)

        import sentry_sdk

        span = sentry_sdk.Hub.current.scope.span
        if span is not None:
            context["SENTRY_TRACE_ID"] = span.to_traceparent()

    return context


def now_tomorrow() -> datetime:
    """Return current time tomorrow."""
    return timezone.now() + timedelta(days=1)


def objectgetter_optional(
    model: Model, default: Optional[Any] = None, default_eval: bool = False
) -> Callable[[HttpRequest, Optional[int]], Model]:
    """Get an object by pk, defaulting to None."""

    def get_object(request: HttpRequest, id_: Optional[int] = None, **kwargs) -> Optional[Model]:
        if id_ is not None:
            return get_object_or_404(model, pk=id_)
        else:
            try:
                return eval(default) if default_eval else default  # noqa:S307
            except (AttributeError, KeyError, IndexError):
                return None

    return get_object


@cache_memoize(3600)
def get_content_type_by_perm(perm: str) -> Union["ContentType", None]:
    from django.contrib.contenttypes.models import ContentType  # noqa

    try:
        return ContentType.objects.get(
            app_label=perm.split(".", 1)[0], permission__codename=perm.split(".", 1)[1]
        )
    except ContentType.DoesNotExist:
        return None


@cache_memoize(3600)
def queryset_rules_filter(
    obj: Union[HttpRequest, Model], queryset: QuerySet, perm: str
) -> QuerySet:
    """Filter queryset by user and permission."""
    wanted_objects = set()
    if isinstance(obj, HttpRequest) and hasattr(obj, "user"):
        obj = obj.user

    for item in queryset:
        if obj.has_perm(perm, item):
            wanted_objects.add(item.pk)

    return queryset.filter(pk__in=wanted_objects)


def generate_random_code(length, packet_size) -> str:
    """Generate random code for e.g. invitations."""
    return get_random_string(packet_size * length).lower()


def monkey_patch() -> None:  # noqa
    """Monkey-patch dependencies for special behaviour."""
    # Unwrap promises in JSON serializer instead of stringifying
    from django.core.serializers import json
    from django.utils.functional import Promise

    class DjangoJSONEncoder(json.DjangoJSONEncoder):
        def default(self, o: Any) -> Any:
            if isinstance(o, Promise) and hasattr(o, "copy"):
                return o.copy()
            return super().default(o)

    json.DjangoJSONEncoder = DjangoJSONEncoder


def get_allowed_object_ids(request: HttpRequest, models: list) -> list:
    """Get all objects of all given models the user of a given request is allowed to view."""
    allowed_object_ids = []

    for model in models:
        app_label = model._meta.app_label
        model_name = model.__name__.lower()

        # Loop through the pks of all objects of the current model the user is allowed to view
        # and put the corresponding ids into a django-haystack-style-formatted list
        allowed_object_ids += [
            f"{app_label}.{model_name}.{pk}"
            for pk in queryset_rules_filter(
                request, model.objects.all(), f"{app_label}.view_{model_name}_rule"
            ).values_list("pk", flat=True)
        ]

    return allowed_object_ids


def process_custom_context_processors(context_processors: list) -> dict[str, Any]:
    """Process custom context processors."""
    context = {}
    processors = tuple(import_string(path) for path in context_processors)
    for processor in processors:
        context.update(processor(None))
    return context


def create_default_celery_schedule():
    """Create default periodic tasks in database for tasks that have a schedule defined."""
    from celery import current_app
    from celery.schedules import BaseSchedule, crontab, schedule, solar
    from django_celery_beat.clockedschedule import clocked
    from django_celery_beat.models import (
        ClockedSchedule,
        CrontabSchedule,
        IntervalSchedule,
        PeriodicTask,
        SolarSchedule,
    )

    defined_periodic_tasks = PeriodicTask.objects.values_list("task", flat=True).all()

    for name, task in current_app.tasks.items():
        if name in defined_periodic_tasks:
            # Task is already known in database, skip
            continue

        run_every = getattr(task, "run_every", None)
        if not run_every:
            # Task has no default schedule, skip
            continue

        if isinstance(run_every, (float, int, timedelta)):
            # Schedule is defined as a raw seconds value or timedelta, convert to schedule class
            run_every = schedule(run_every)
        elif not isinstance(run_every, BaseSchedule):
            raise ValueError(f"Task {name} has an invalid schedule defined.")

        # Find matching django-celery-beat schedule model
        if isinstance(run_every, clocked):
            Schedule = ClockedSchedule
            attr = "clocked"
        elif isinstance(run_every, crontab):
            Schedule = CrontabSchedule
            attr = "crontab"
        elif isinstance(run_every, schedule):
            Schedule = IntervalSchedule
            attr = "interval"
        elif isinstance(run_every, solar):
            Schedule = SolarSchedule
            attr = "solar"
        else:
            raise ValueError(f"Task {name} has an unknown schedule class defined.")

        # Get or create schedule in database
        db_schedule = Schedule.from_schedule(run_every)
        db_schedule.save()

        # Create periodic task
        PeriodicTask.objects.create(
            name=f"{name} (default schedule)", task=name, **{attr: db_schedule}
        )


class OOTRouter:
    """Database router for operations that should run out of transaction.

    This router routes database operations for certain apps through
    the separate default_oot connection, to ensure that data get
    updated immediately even during atomic transactions.
    """

    default_db = "default"
    oot_db = "default_oot"

    @property
    def oot_labels(self):
        return settings.DATABASE_OOT_LABELS

    @property
    def default_dbs(self):
        return set((self.default_db, self.oot_db))

    def is_same_db(self, db1: str, db2: str):
        return set((db1, db2)).issubset(self.default_dbs)

    def db_for_read(self, model: Model, **hints) -> Optional[str]:
        if model._meta.app_label in self.oot_labels:
            return self.oot_db

        return None

    def db_for_write(self, model: Model, **hints) -> Optional[str]:
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1: Model, obj2: Model, **hints) -> Optional[bool]:
        # Allow relations between default database and OOT connection
        # They are the same database
        if self.is_same_db(obj1._state.db, obj2._state.db):
            return True

        return None

    def allow_migrate(
        self, db: str, app_label: str, model_name: Optional[str] = None, **hints
    ) -> Optional[bool]:
        # Never allow any migrations on the default_oot database
        # It connects to the same database as default, so everything
        # migrated there
        if db == self.oot_db:
            return False

        return None


def get_ip(*args, **kwargs):
    """Recreate ipware.ip.get_ip as it was replaced by get_client_ip."""
    from ipware.ip import get_client_ip  # noqa

    return get_client_ip(*args, **kwargs)[0]


EXTENDED_FEED_FIELD_MAP = feedgenerator.FEED_FIELD_MAP + (("color", "color"),)
EXTENDED_ITEM_ELEMENT_FIELD_MAP = feedgenerator.ITEM_ELEMENT_FIELD_MAP + (
    ("color", "color"),
    ("meta", "x-meta"),
    ("reference_object", "reference_object"),
)


class ExtendedICal20Feed(feedgenerator.ICal20Feed):
    """Extends the ICal20Feed class from django-ical.

    Adds a method to return the actual calendar object.
    """

    def _is_unrequested_prop(
        self, element: Component, efield: str, params: Optional[dict[str, any]] = None
    ):
        """Return True if specific fields are requested and efield is not one of those.
        If no fields are specified or efield is requested, return False"""

        return (
            params is not None
            and element.name in params
            and efield is not None
            and efield.upper() not in params[element.name]
        )

    def get_calendar_object(
        self,
        with_meta: bool = True,
        with_reference_object: bool = False,
        params: dict[str, any] = None,
    ):
        cal = Calendar()
        cal_props = {
            "version": "2.0",
            "calscale": "GREGORIAN",
            "prodid": "-//AlekSIS//AlekSIS//EN",
        }
        for efield, val in cal_props.items():
            if self._is_unrequested_prop(cal, efield, params):
                continue

            cal.add(efield, val)

        for ifield, efield in EXTENDED_FEED_FIELD_MAP:
            if self._is_unrequested_prop(cal, efield, params):
                continue

            val = self.feed.get(ifield)
            if val:
                cal.add(efield, val)

        self.write_items(
            cal, with_meta=with_meta, with_reference_object=with_reference_object, params=params
        )

        if params is not None and "VTIMEZONE" in params and params["VTIMEZONE"]:
            cal.add_missing_timezones()

        return cal

    def to_ical(self, params: Optional[dict[str, any]] = None):
        cal = self.get_calendar_object(with_meta=False, params=params)

        to_ical = getattr(cal, "as_string", None)
        if not to_ical:
            to_ical = cal.to_ical
        return to_ical()

    def write(self, outfile, params: Optional[dict[str, any]] = None):
        cal = self.get_calendar_object(with_meta=False, params=params)

        to_ical = getattr(cal, "as_string", None)
        if not to_ical:
            to_ical = cal.to_ical
        outfile.write(self.to_ical())

    def write_items(
        self,
        calendar,
        with_meta: bool = True,
        with_reference_object: bool = False,
        params: dict[str, any] = None,
    ):
        if params is not None and "timezone" in params:
            tz = Timezone.from_ical(params["timezone"])
        else:
            tz = None

        for item in self.items:
            component_type = item.get("component_type")
            if component_type == "todo":
                element = Todo()
            elif component_type == "freebusy":
                element = FreeBusy()
            else:
                element = Event()

            for ifield, efield in EXTENDED_ITEM_ELEMENT_FIELD_MAP:
                if self._is_unrequested_prop(element, efield, params):
                    continue

                val = item.get(ifield)

                if val:
                    if ifield == "attendee" or ifield == "related_to":
                        for list_item in val:
                            element.add(efield, list_item)
                    elif ifield == "valarm":
                        for list_item in val:
                            element.add_component(list_item)
                    elif ifield == "meta":
                        if with_meta:
                            element.add(efield, json.dumps(val))
                    elif ifield == "reference_object":
                        if with_reference_object:
                            element.add(efield, val, encode=False)
                    elif (
                        ifield == "start_datetime"
                        or ifield == "end_datetime"
                        or ifield == "timestamp"
                        or ifield == "created"
                        or ifield == "updateddate"
                        or ifield == "rdate"
                        or ifield == "exdate"
                    ):
                        if tz is not None:
                            val = val.astimezone(tz.to_tz())
                        element.add(efield, val)
                    else:
                        element.add(efield, val)
            calendar.add_component(element)

        if params is not None and ("expand_start" in params and "expand_end" in params):
            recurrences = self.get_single_events(
                start=params["expand_start"],
                end=params["expand_end"],
            )

            for event in recurrences:
                props = list(event.keys())
                for prop in props:
                    if self._is_unrequested_prop(event, prop, params):
                        event.pop(prop)
                calendar.add_component(event)


def get_active_school_term(request):
    from ..models import SchoolTerm

    if request is not None:
        pk = request.session.get("active_school_term", None)

        if pk is not None:
            return SchoolTerm.objects.get(pk=pk)

    return SchoolTerm.current


def filter_active_school_term(
    request,
    q,
    school_term_field="school_term",
):
    if active_school_term := get_active_school_term(request):
        return q.filter(
            Q(**{school_term_field: active_school_term}) | Q(**{school_term_field: None})
        )
    return q


def filter_active_school_term_by_date(
    request: HttpRequest,
    qs: QuerySet,
    date_start_field: str = "date_start",
    date_end_field: str = "date_end",
    datetime_start_field: str = "datetime_start",
    datetime_end_field: str = "datetime_end",
) -> QuerySet:
    """Filter all objects within the school term, based on their start and end dates."""
    if active_school_term := get_active_school_term(request):
        return qs.filter(
            Q(
                **{
                    f"{date_start_field}__lte": active_school_term.date_end,
                    f"{date_end_field}__gte": active_school_term.date_start,
                }
            )
            | Q(
                **{
                    f"{datetime_start_field}__date__lte": active_school_term.date_end,
                    f"{datetime_end_field}__date__gte": active_school_term.date_start,
                }
            )
        )
    return qs


def get_preferred_vcard_version(
    request: Optional[HttpRequest] = None, params: Optional[dict[str, any]] = None
):
    if params is None or "vcard_version" not in params:
        version = "4.0"
        if request is not None and (accept := request.headers.get("Accept", None)) is not None:
            if "version=" in accept:
                version = next(
                    filter(lambda x: x.params.get("version", False), request.accepted_types)
                ).params.get("version")
            elif "text/vcard" not in accept:
                version = "3.0"
        params = {"vcard_version": version}

    if (vcard_version := params.get("vcard_version", "4.0")) not in ("3.0", "4.0"):
        raise ValueError(f"Requested vCard version ({vcard_version}) is not supported.")

    return vcard_version
