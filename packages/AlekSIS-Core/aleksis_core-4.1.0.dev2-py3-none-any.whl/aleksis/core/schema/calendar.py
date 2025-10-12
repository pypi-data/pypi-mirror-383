import json
from datetime import datetime, time

from django.core.exceptions import PermissionDenied
from django.urls import reverse

import graphene
from graphene import ObjectType

from aleksis.core.mixins import CalendarEventMixin
from aleksis.core.util.core_helpers import has_person


class CalendarEventType(ObjectType):
    name = graphene.String()
    description = graphene.String()
    location = graphene.String(required=False)
    start = graphene.DateTime()
    end = graphene.DateTime()
    color = graphene.String()
    uid = graphene.String()
    all_day = graphene.Boolean()
    status = graphene.String()
    meta = graphene.String()
    freebusy = graphene.String()
    fbtype = graphene.String()

    percent_complete = graphene.Int(required=False)
    completed = graphene.DateTime(required=False)
    due = graphene.DateTime(required=False)

    def resolve_name(root, info, **kwargs):
        return root["SUMMARY"]

    def resolve_description(root, info, **kwargs):
        return root.get("DESCRIPTION", "")

    def resolve_location(root, info, **kwargs):
        return root.get("LOCATION", "")

    def resolve_start(root, info, **kwargs):
        return root["DTSTART"].dt

    def resolve_end(root, info, **kwargs):
        return root["DTEND"].dt

    def resolve_color(root, info, **kwargs):
        return root.get("COLOR")

    def resolve_uid(root, info, **kwargs):
        return root["UID"]

    def resolve_all_day(root, info, **kwargs):
        return not isinstance(root["DTSTART"].dt, datetime)

    def resolve_status(root, info, **kwargs):
        return root.get("STATUS", "")

    def resolve_meta(root, info, **kwargs):
        return root.get("X-META", "{}")

    def resolve_freebusy(root, info, **kwargs):
        return root.get("FREEBUSY", "")

    def resolve_fbtype(root, info, **kwargs):
        freebusy = root.get("FREEBUSY")
        if freebusy:
            return freebusy.params["FBTYPE"]
        return ""

    def resolve_percent_complete(root, info, **kwargs):
        return root.get("PERCENT-COMPLETE")

    def resolve_completed(root, info, **kwargs):
        completed = root.get("COMPLETED")
        if completed:
            return completed.dt
        return None

    def resolve_due(root, info, **kwargs):
        due = root.get("DUE")
        if due:
            return due.dt
        return None


class CalendarType(ObjectType):
    name = graphene.String(required=True)
    verbose_name = graphene.String(required=True)
    description = graphene.String()
    events = graphene.List(
        CalendarEventType,
        start=graphene.Date(required=False),
        end=graphene.Date(required=False),
        datetime_start=graphene.DateTime(required=False),
        datetime_end=graphene.DateTime(required=False),
        params=graphene.String(required=False),
        expand=graphene.Boolean(required=False),
    )

    def resolve_events(
        root,
        info,
        start=None,
        end=None,
        datetime_start=None,
        datetime_end=None,
        params=None,
        expand=True,
        **kwargs,
    ):
        if params:
            params = json.loads(params)
        if datetime_start:
            start = datetime_start
        elif start:
            start = datetime.combine(start, time.min)
        if datetime_end:
            end = datetime_end
        elif end:
            end = datetime.combine(end, time.max)

        return root.get_single_events(start, end, info.context, params, expand=expand)

    color = graphene.String()

    url = graphene.String()

    activated = graphene.Boolean()

    component_type = graphene.String()

    def resolve_name(root, info, **kwargs):
        return root._class_name

    def resolve_verbose_name(root, info, **kwargs):
        return root.get_verbose_name(info.context)

    def resolve_description(root, info, **kwargs):
        return root.get_description(info.context)

    def resolve_url(root, info, **kwargs):
        return info.context.build_absolute_uri(
            reverse("calendar_feed", args=["calendar", root._class_name])
        )

    def resolve_color(root, info, **kwargs):
        return root.get_color(info.context)

    def resolve_activated(root, info, **kwargs):
        return root.get_activated(info.context.user.person)

    def resolve_component_type(root, info, **kwargs):
        return root.value_component_type(None)


class SetCalendarStatusMutation(graphene.Mutation):
    """Mutation to change the status of a calendar."""

    class Arguments:
        calendars = graphene.List(graphene.String)

    ok = graphene.Boolean()

    def mutate(root, info, calendars, **kwargs):
        if not has_person(info.context):
            raise PermissionDenied
        calendar_feeds = [cal for cal in calendars if cal in CalendarEventMixin.valid_feed_names]
        info.context.user.person.preferences["calendar__activated_calendars"] = calendar_feeds
        return SetCalendarStatusMutation(ok=True)


class CalendarBaseType(ObjectType):
    calendar_feeds = graphene.List(
        CalendarType, names=graphene.List(graphene.String, required=False)
    )

    all_feeds_url = graphene.String()

    def resolve_calendar_feeds(root, info, names=None, **kwargs):
        if not has_person(info.context.user):
            return []
        if names is not None:
            feeds = [CalendarEventMixin.get_object_by_name(name) for name in names]
            return [feed for feed in feeds if feed.get_enabled(info.context)]
        return CalendarEventMixin.get_overview_feeds(info.context)

    def resolve_all_feeds_url(root, info, **kwargs):
        return info.context.build_absolute_uri(reverse("all_calendar_feeds", args=["calendar"]))
