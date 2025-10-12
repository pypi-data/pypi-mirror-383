from datetime import datetime
from xml.etree import ElementTree

from django.db.models import Q
from django.http import Http404
from django.urls import reverse

from ..core_helpers import EXTENDED_ITEM_ELEMENT_FIELD_MAP
from .base import ElementHandler, QueryBase
from .generic import DAVHref, DAVProp


class TimeRangeFilter(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}time-range"
    invisible = True

    def post_handle(self):
        report_base = next(iter(self.request.children))

        for k, v in self.attrs.items():
            if k in [(None, "start"), (None, "end")]:
                d = datetime.fromisoformat(v)
                report_base.get_objects_args[k[1]] = d


class TextMatch(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}text-match"
    invisible = True

    def _matches(self, obj, field_name):
        method_name = f"value_{field_name}"
        if not hasattr(obj, method_name) or not callable(getattr(obj, method_name)):
            return False

        return self.content.lower() in getattr(obj, method_name)(obj)  # FIXME: Collations

    def post_handle(self):
        field_name = self.parent._get_field_name(self.parent.attrs.get((None, "name")))
        objs = [
            obj.pk
            for obj in filter(lambda obj: self._matches(obj, field_name), self.request.objects)
        ]
        q = Q(pk__in=[objs])

        report_base = next(iter(self.request.children))

        if "additional_filter" in report_base.get_objects_args:
            q = report_base.get_objects_args["additional_filter"] & q

        report_base.get_objects_args["additional_filter"] = q


class PropFilter(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}prop-filter"
    invisible = True

    @staticmethod
    def _get_field_name(ical_name):
        fields = list(filter(lambda f: f[1] == ical_name.lower(), EXTENDED_ITEM_ELEMENT_FIELD_MAP))
        try:
            return fields.pop()[0]
        except StopIteration:
            return None


class CalDAVProp(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}prop"
    invisible = True

    @classmethod
    def get_name(cls, attrs):
        name = attrs.get((None, "name"))
        return f"{cls._class_name}-{name}"

    def _get_calendar_data(self, parent):
        """Helper method to find the base `CalendarData` instance."""

        if isinstance(parent, CalendarData):
            return parent
        return self._get_calendar_data(parent.parent)

    def pre_handle(self):
        calendar_data = self._get_calendar_data(self.parent.parent)
        comp_name = self.parent.attrs.get((None, "name"))
        prop = self.attrs.get((None, "name"))
        calendar_data.params.setdefault(comp_name, []).append(prop)


class CalDAVFilter(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}filter"
    invisible = True

    def pre_handle(self):
        self.filters = {}


class CalDAVCompFilter(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}comp-filter"
    invisible = True


class CalDAVComp(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}comp"
    invisible = True

    @classmethod
    def get_name(cls, attrs):
        name = attrs.get((None, "name"))
        return f"{cls._class_name}-{name}"

    def pre_handle(self):
        if self.attrs.get((None, "name")) == "VTIMEZONE":
            self.parent.parent.params["VTIMEZONE"] = True


class Expand(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}expand"

    def post_handle(self):
        for k, v in self.attrs.items():
            if k in [(None, "start"), (None, "end")]:
                d = datetime.fromisoformat(v)
                self.parent.params[f"expand_{k[1]}"] = d


class CalendarData(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}calendar-data"

    def pre_handle(self):
        self.params = {}

    def post_handle(self):
        if not self.params:
            attrs = {(None, "name"): "VCALENDAR"}
            vcalendar = CalDAVComp(self.request, self, attrs)
            self.children.append(vcalendar)

            self.params["VTIMEZONE"] = True

            for comp_name in ("VTIMEZONE", "VEVENT"):
                attrs = {(None, "name"): comp_name}
                comp = CalDAVComp(self.request, self, attrs)
                vcalendar.children.append(comp)

    def process_xml(self, base, response):
        super().process_xml(base, response)
        if not self.invisible:
            if response.obj is not None:
                objects = response.resource.objects.filter(pk=response.obj.pk)
            else:
                objects = []

            ical = response.resource.get_dav_file_content(
                base.request._request, objects, params=self.params
            )
            base.current_xml.text = ical.decode()


class CalendarColor(ElementHandler):
    _class_name = "{http://apple.com/ns/ical/}calendar-color"

    def process_xml(self, base, response):
        if not hasattr(response.resource, "get_color"):
            raise Http404

        super().process_xml(base, response)
        base.current_xml.text = response.resource.get_color(self.request._request)


class CalendarDescription(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}calendar-description"

    def process_xml(self, base, response):
        if not hasattr(response.resource, "get_description"):
            raise Http404

        super().process_xml(base, response)
        base.current_xml.text = response.resource.get_description()


class CalendarHomeSet(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}calendar-home-set"

    def process_xml(self, base, response):
        super().process_xml(base, response)
        href = ElementTree.SubElement(base.current_xml, "{DAV:}href")
        href.text = reverse("dav_subregistry", args=["calendar"])


class SupportedCalendarComponentSet(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}supported-calendar-component-set"

    def process_xml(self, base, response):
        super().process_xml(base, response)
        comp = ElementTree.SubElement(base.current_xml, "{urn:ietf:params:xml:ns:caldav}comp")
        # In AlekSIS, a calendar can only provide one type of component.
        # Therefore, the value is independent from a specific instance,
        # so that reference_object can be None.
        component_types = {
            "event": "VEVENT",
            "todo": "VTODO",
            "freebusy": "VFREEBUSY",
        }
        comp.set("name", component_types[response.resource.value_component_type(None)])


class SupportedCollationSet(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}supported-collation-set"

    def process_xml(self, base, response):
        super().process_xml(base, response)

        supported_collations = [
            "i;ascii-casemap",
            "i;octet",
        ]

        for collation in supported_collations:
            supported_collation = ElementTree.SubElement(
                base.current_xml, "{urn:ietf:params:xml:ns:caldav}supported-collation"
            )
            supported_collation.text = collation


class Timezone(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}timezone"
    invisible = True


class ReportBase(QueryBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.get_objects_args = {
            "request": self.request._request,
        }

    def post_handle(self):
        super().post_handle()

        try:
            timezone = next(filter(lambda child: isinstance(child, Timezone), self.children))
        except StopIteration:
            timezone = None

        if timezone is not None:
            prop = next(filter(lambda child: isinstance(child, DAVProp), self.children))
            calendar_data = next(
                filter(lambda child: isinstance(child, CalendarData), prop.children)
            )
            calendar_data.params["timezone"] = timezone.content


class CalendarQuery(ReportBase, ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}calendar-query"

    def pre_handle(self):
        self.request.resources = []

    def post_handle(self):
        self.request.objects = self.request.resource.get_objects(**self.get_objects_args)


class CalendarMultiget(ReportBase, ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:caldav}calendar-multiget"

    def pre_handle(self):
        self.request.resources = []
        self.request.objects = []

    def post_handle(self):
        super().post_handle()

        for child in self.children:
            if child._class_name == DAVHref._class_name:
                child.invisible = True
