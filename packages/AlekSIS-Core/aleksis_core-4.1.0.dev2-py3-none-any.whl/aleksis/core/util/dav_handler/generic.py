from xml.etree import ElementTree

from django.core.cache import cache
from django.http import Http404
from django.urls import resolve

from ...mixins import DAVResource
from .base import DAVMultistatus, DAVResponse, ElementHandler, NotFoundObject, QueryBase


class DAVEtag(ElementHandler):
    _class_name = "{DAV:}getetag"

    def process_xml(self, base, response):
        super().process_xml(base, response)
        objects = [response.obj] if response.obj is not None else []
        etag = response.resource.getetag(base.request._request, objects)
        base.current_xml.text = f'"{etag}"'


class DAVDisplayname(ElementHandler):
    _class_name = "{DAV:}displayname"

    def process_xml(self, base, response):
        super().process_xml(base, response)
        base.current_xml.text = response.resource.get_dav_verbose_name()


class DAVResourcetype(ElementHandler):
    _class_name = "{DAV:}resourcetype"

    def process_xml(self, base, response):
        super().process_xml(base, response)
        resource_types = ["{DAV:}collection"]
        if not getattr(response.resource, "_is_registry", False):
            resource_types += response.resource.dav_resource_types

        if response.obj is None:
            for res_type_attr in resource_types:
                ElementTree.SubElement(base.current_xml, res_type_attr)


class DAVCurrentUserPrincipal(ElementHandler):
    _class_name = "{DAV:}current-user-principal"

    def process_xml(self, base, response):
        super().process_xml(base, response)
        href = ElementTree.SubElement(base.current_xml, "{DAV:}href")
        person_pk = base.request._request.user.person.pk
        href.text = f"/dav/contact/person/{person_pk}.vcf"  # FIXME: Implement principals


class DAVGetcontenttype(ElementHandler):
    _class_name = "{DAV:}getcontenttype"

    def process_xml(self, base, response):
        resource = response.resource
        if response.obj is not None:
            resource = response.obj
        content_type = resource.get_dav_content_type()

        if not content_type:
            raise Http404

        super().process_xml(base, response)
        base.current_xml.text = content_type


class DAVGetcontentlength(ElementHandler):
    _class_name = "{DAV:}getcontentlength"

    def process_xml(self, base, response):
        obj = response.obj
        if obj is None:
            raise Http404

        super().process_xml(base, response)

        key = f"{obj._class_name}_{obj.pk}_dav_contentlength"
        if (cached := cache.get(key, None)) is not None:
            contentlength = cached
        else:
            contentlength = len(
                response.resource.get_dav_file_content(base.request._request, [obj])
            )
            cache.set(key, contentlength, 60 * 60 * 24)

        base.current_xml.text = str(contentlength)


class DAVSupportedReportSet(ElementHandler):
    _class_name = "{DAV:}supported-report-set"

    def process_xml(self, base, response):
        super().process_xml(base, response)

        supported_reports = [
            ("urn:ietf:params:xml:ns:caldav", "calendar-multiget"),
            ("urn:ietf:params:xml:ns:caldav", "calendar-query"),
        ]

        for r in supported_reports:
            supported_report = ElementTree.SubElement(base.current_xml, "{DAV:}supported-report")
            report = ElementTree.SubElement(supported_report, "{DAV:}report")
            ElementTree.SubElement(report, self._get_xml_sub(r))


class DAVCurrentUserPrivilegeSet(ElementHandler):
    _class_name = "{DAV:}current-user-privilege-set"

    def process_xml(self, base, response):
        super().process_xml(base, response)

        privileges = [
            ("DAV:", "read"),
        ]

        for p in privileges:
            privilege = ElementTree.SubElement(base.current_xml, "{DAV:}privilege")
            ElementTree.SubElement(privilege, self._get_xml_sub(p))


class DAVHref(ElementHandler):
    _class_name = "{DAV:}href"

    def post_handle(self):
        res = resolve(self.content)
        name = res.kwargs.get("name")
        pk = res.kwargs.get("id")

        resource = DAVResource.registered_objects_dict[name]
        try:
            obj = resource.get_objects(self.request._request).get(pk=pk)
        except resource.DoesNotExist:
            obj = NotFoundObject(self.content)

        self.request.objects = list(self.request.objects)
        self.request.objects.append(obj)


class DAVProp(ElementHandler):
    _class_name = "{DAV:}prop"


class DAVPropname(ElementHandler):
    _class_name = "{DAV:}propname"
    invisible = True

    def process_xml(self, base: DAVMultistatus, response: DAVResponse = None):
        base.current_xml = ElementTree.SubElement(base.current_xml, DAVProp._class_name)

        response.resource._add_dav_propnames(base.current_xml)


class DAVAllprop(ElementHandler):
    _class_name = "{DAV:}allprop"
    invisible = True

    def pre_handle(self):
        for name in self.request.resource.dav_live_props:
            self.request.startElementNS(name, None, {})
            self.request.endElementNS(name, None)

    def process(self, stage: str, base: DAVMultistatus, response: DAVResponse = None):
        xml_element = base.current_xml.find(DAVProp._class_name)
        if xml_element is not None:
            base.current_xml = xml_element

        super().process(stage, base, response)

    def process_xml(self, base: DAVMultistatus, response: DAVResponse = None):
        base.current_xml = ElementTree.SubElement(base.current_xml, DAVProp._class_name)


class Propfind(QueryBase, ElementHandler):
    _class_name = "{DAV:}propfind"
    invisible = True

    def post_handle(self):
        super().post_handle()

        _is_registry = getattr(self.request.resource, "_is_registry", False)

        if not _is_registry or self.request.depth is None:
            for resource in filter(
                lambda r: not getattr(r, "_is_registry", False), self.request.resources
            ):
                try:
                    objs = resource.get_objects(self.request._request)
                except NotImplementedError:
                    objs = []

                self.request.objects += objs
