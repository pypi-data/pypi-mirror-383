import warnings
from typing import Optional
from xml.etree import ElementTree
from xml.sax.handler import ContentHandler, feature_namespaces
from xml.sax.xmlreader import InputSource

from django.core.exceptions import BadRequest
from django.http import Http404, HttpRequest
from django.urls import reverse

from defusedxml.sax import make_parser

from ...mixins import DAVResource, RegistryObject


class ElementHandler(RegistryObject, is_registry=True):
    """Abstract class serving as registry for ElementHandlers.

    While parsing an XML document, for every XML element a handler exists for,
    an instance of the respective sub class is created. By using the `children`
    attribute, the tree is represented for later processing and creating the
    response. Using `invisible` causes the Element not to be included in XML.
    """

    invisible: bool = False

    def __init__(
        self,
        request: "DAVRequest",
        parent: "ElementHandler",
        attrs,
        invisible: Optional[bool] = None,
    ):
        self.request = request
        self.parent = parent
        self.attrs = attrs
        self.content = ""
        if invisible is not None:
            self.invisible = invisible
        else:
            self.invisible = self.__class__.invisible
        self.children = []

    @classmethod
    def get_name(cls, attrs):
        return cls._class_name

    def continueToChild(self, child_class, attrs, invisible: Optional[bool] = None):
        """Create instance of ElementHandler `child_class` and append to
        children or return existing child."""

        child = child_class(self.request, self, attrs, invisible=invisible)
        self.children.append(child)
        self.request.current_object = child

        return child

    def process(self, stage: str, base: "DAVMultistatus", response: "DAVResponse" = None):
        """Build elements of the DAV multistatus response."""

        previous_xml = base.current_xml

        if not self.invisible:
            xml_element = base.current_xml.find(self._class_name)
            if xml_element is not None:
                base.current_xml = xml_element

        stage_method_name = f"process_{stage}"
        if hasattr(self, stage_method_name) and callable(
            stage_method := getattr(self, stage_method_name)
        ):
            try:
                stage_method(base, response)
            except Http404:
                response.handle_unknown(self._class_name)

        for child in self.children:
            child.process(stage, base, response)

        base.current_xml = previous_xml

    def process_xml(self, base: "DAVMultistatus", response: "DAVResponse" = None):
        """Add XML element representing self to multistatus XML tree."""

        if not self.invisible:
            base.current_xml = ElementTree.SubElement(base.current_xml, self._class_name)

    @staticmethod
    def _get_xml_sub(name):
        """Convert a tuple like ("DAV:", "prop") to a string like "{DAV:}prop"."""

        return f"{{{name[0]}}}{name[1]}"


class DAVRequest(ElementHandler, ContentHandler):
    """Handler that processes a DAV Request by parsing its XML tree.

    Based on the `resource`, `obj` and `depth`, `resources` and `objects` to be
    included the response are determined.  Furthermore, `ElementHandler`s may
    modify those.
    """

    depth: int | None

    def __init__(
        self, http_request: HttpRequest, resource: type[DAVResource], obj: Optional[DAVResource]
    ):
        super().__init__(self, None, {})
        self._request = http_request

        if depth := self._request.headers.get("Depth", "infinity"):
            if depth not in ("0", "1", "infinity"):
                raise BadRequest("Depth must be 0, 1 or infinity")
            elif depth == "infinity":
                self.depth = None
            else:
                self.depth = int(depth)

        self.current_object = self

        self.resource = resource
        self.resources = []
        self.objects = []

        _is_registry = getattr(self.resource, "_is_registry", False)

        if obj is None:
            self.resources.append(self.resource)

            if self.depth != 0 and _is_registry:
                resources = []
                if self.resource == DAVResource:
                    resources += self.resource.get_sub_registries().values()
                if self.resource != DAVResource or self.depth is None:
                    if hasattr(self.resource, "valid_feeds"):
                        resources += self.resource.valid_feeds
                    else:
                        resources += self.resource.get_registry_objects().values()

                for rcls in resources:
                    self.resources.append(rcls)

        else:
            self.objects.append(obj)

    def parse(self):
        """Start parsing the event-based XML parser."""

        parser = make_parser()
        parser.setFeature(feature_namespaces, True)
        parser.setContentHandler(self)

        source = InputSource()
        source.setByteStream(self._request)
        return parser.parse(source)

    def startElementNS(self, name, qname, attrs):
        """Handle start of a new XML element and continue to respective handler.

        `ElementHandler`s may implement a `pre_handle` method to be called at
        the start of an element.
        """

        xml_sub = self._get_xml_sub(name)
        obj = self.get_object_by_name(xml_sub)
        if obj is not None:
            self.current_object.continueToChild(obj, attrs.copy())
            if hasattr(obj, "pre_handle"):
                self.current_object.pre_handle()
        else:
            child = NotImplementedObject(xml_sub)
            self.current_object.children.append(child)
            warnings.warn(f"DAVRequest could not parse {xml_sub}.")

    def endElementNS(self, name, qname):
        """Handle end of an  XML element.

        `ElementHandler`s may implement a `post_handle` method to be called at
        the end of an element.
        """

        if self.current_object._class_name == self._get_xml_sub(name):
            if hasattr(self.current_object, "post_handle"):
                self.current_object.post_handle()
            self.current_object = self.current_object.parent

    def characters(self, content):
        """Handle content of an XML element."""

        self.current_object.content += content


class DAVMultistatus:
    """Base of a DAV multistatus response.

    Processes children of DAVRequest `request` to build response XML.
    """

    _class_name = "{DAV:}multistatus"

    def __init__(self, request: DAVRequest):
        self.request = request

        self.request.resource._register_dav_ns()
        self.xml_element = ElementTree.Element(self._class_name)
        self.current_xml = self.xml_element

    def process(self):
        """Call process stages of all `children` of a `DAVRequest`.

        There are the following stages, optionally implemented
        by ElementHandlers using methods named `process_{stage}`:
        `xml`: Build the response by adding an element to the XML tree.
        """

        for stage in ("xml",):
            for child in self.request.children:
                child.process(stage, self)


class NotImplementedObject:
    """Class to represent requested props that are not implemented."""

    def __init__(self, xml_sub):
        self.xml_sub = xml_sub

    def process(self, stage, base, response=None):
        if stage == "xml" and response is not None:
            response.handle_unknown(self.xml_sub)


class NotFoundObject:
    """Class to represent requested objects that do not exist."""

    def __init__(self, href):
        self.href = href


class DAVResponse:
    """Part of a `DAVMultistatus` containing props of a single `resource` or `obj`."""

    _class_name = "{DAV:}response"

    def __init__(self, base: "DAVMultistatus", resource, obj):  # noqa: F821
        self.base = base
        self.resource = resource
        self.obj = obj

        self.xml_element = ElementTree.SubElement(self.base.current_xml, self._class_name)

        self.href = ElementTree.SubElement(self.xml_element, "{DAV:}href")

        if obj is None:
            if self.resource == DAVResource:
                self.href.text = reverse("dav_registry")
            elif getattr(self.resource, "_is_registry", False):
                self.href.text = reverse("dav_subregistry", args=[self.resource._class_name])
            else:
                self.href.text = reverse(
                    "dav_resource",
                    args=[self.resource.__bases__[0]._class_name, self.resource._class_name],
                )
        else:
            if isinstance(obj, NotFoundObject):
                self.href.text = obj.href
            else:
                self.href.text = self.resource.get_dav_absolute_url(
                    self.obj, self.base.request._request
                )

        self.propstats = {}

        if isinstance(obj, NotFoundObject):
            status = ElementTree.SubElement(self.xml_element, "{DAV:}status")
            status.text = "HTTP/1.1 404 Not Found"
        else:
            self.init_propstat(200, "HTTP/1.1 200 OK")

    def init_propstat(self, code, status_text):
        """Initialize common sub elements of a DAV response."""

        propstat = ElementTree.SubElement(self.xml_element, "{DAV:}propstat")
        status = ElementTree.SubElement(propstat, "{DAV:}status")
        status.text = status_text

        self.propstats[code] = propstat
        return propstat

    def handle_unknown(self, xml_sub):
        """Handle element for which no `ElementHandler` exists."""

        if 404 not in self.propstats:
            propstat = self.init_propstat(404, "HTTP/1.1 404 Not Found")
            ElementTree.SubElement(propstat, "{DAV:}prop")

        propstat = self.propstats[404]
        prop = propstat.find("{DAV:}prop")
        ElementTree.SubElement(prop, xml_sub)


class QueryBase:
    """Mixin for REPORT or PROPFIND query `ElementHandler`s.

    Creates `DAVResponse` objects for `resources` and `objects` of a
    `DAVRequest` to be processed in order to build the response.
    """

    def process(self, stage: str, base):
        """Custom process method calling `children`'s process methods for each
        response."""

        previous_xml = base.current_xml

        stage_method_name = f"process_{stage}"
        if hasattr(self, stage_method_name) and callable(
            stage_method := getattr(self, stage_method_name)
        ):
            stage_method(base)

        for response in self.responses:
            if isinstance(response.obj, NotFoundObject):
                continue

            base.current_xml = response.propstats[200]
            for child in self.children:
                child.process(stage, base, response)

        base.current_xml = previous_xml

    def process_xml(self, base):
        self.responses = []
        for resource in base.request.resources:
            response = DAVResponse(base, resource, None)
            self.responses.append(response)

        for obj in base.request.objects:
            response = DAVResponse(base, base.request.resource, obj)
            self.responses.append(response)

    def post_handle(self):
        if self.request.objects is None:
            self.request.objects = self.request.resource.get_objects(
                request=self.request._request, start_qs=self.request.objects
            )
