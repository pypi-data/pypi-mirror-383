from xml.etree import ElementTree

from django.http import Http404
from django.urls import reverse

from .base import ElementHandler, QueryBase
from .generic import DAVHref


class CardDAVProp(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:carddav}prop"
    invisible = True

    @classmethod
    def get_name(cls, attrs):
        name = attrs.get((None, "name"))
        return f"{cls._class_name}-{name}"

    def _get_address_data(self, parent):
        """Helper method to find the base `AddressData` instance."""

        if isinstance(parent, AddressData):
            return parent
        return self._get_address_data(parent.parent)

    def pre_handle(self):
        address_data = self._get_address_data(self.parent)
        comp_name = "VCARD"
        prop = self.attrs.get((None, "name"))
        address_data.params.setdefault(comp_name, []).append(prop)


class AddressData(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:carddav}address-data"

    def pre_handle(self):
        if "content-type" not in self.attrs:
            self.params = {}
        else:
            accepted_content_type = self.attrs.get((None, "content-type"), "text/vcard")
            if accepted_content_type == "text/directory":
                accepted_version = "3.0"
            else:
                accepted_version = self.attrs.get((None, "version"), "4.0")

            self.params["vcard_version"] = accepted_version

    def process_xml(self, base, response):
        super().process_xml(base, response)
        if not self.invisible:
            objects = [response.obj] if response.obj is not None else []
            vcf = response.resource.get_dav_file_content(
                base.request._request, objects, params=self.params
            )
            base.current_xml.text = vcf.decode()


class AddressbookDescription(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:carddav}addressbook-description"

    def process_xml(self, base, response):
        if not hasattr(response.resource, "get_description"):
            raise Http404

        response.resource.get_description()
        base.current_xml.text = response.resource.get_description()
        super().process_xml(base, response)


class AddressbookHomeSet(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:carddav}addressbook-home-set"

    def process_xml(self, base, response):
        super().process_xml(base, response)
        href = ElementTree.SubElement(base.current_xml, "{DAV:}href")
        href.text = reverse("dav_subregistry", args=["contact"])


class SupportedAddressData(ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:carddav}supported-address-data"

    def process_xml(self, base, response):
        super().process_xml(base, response)
        for version in ["3.0", "4.0"]:
            comp = ElementTree.SubElement(
                base.current_xml, "{urn:ietf:params:xml:ns:carddav}address-data-type"
            )
            comp.set("content-type", "text/vcard")
            comp.set("version", version)


class AddressbookQuery(QueryBase, ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:carddav}addressbook-query"

    def pre_handle(self):
        self.request.resources = []


class AddressbookMultiget(QueryBase, ElementHandler):
    _class_name = "{urn:ietf:params:xml:ns:carddav}addressbook-multiget"

    def pre_handle(self):
        self.request.resources = []
        self.request.objects = []

    def post_handle(self):
        for child in self.children:
            if child._class_name == DAVHref._class_name:
                child.invisible = True
