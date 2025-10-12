# flake8: noqa: DJ12

import os
import warnings
from collections.abc import Iterable, Sequence
from datetime import datetime
from hashlib import sha256
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Optional, Union
from urllib.parse import parse_qs, urljoin
from xml.etree import ElementTree

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView, RedirectURLMixin
from django.core.cache import cache
from django.core.exceptions import BadRequest
from django.db import models
from django.db.models import JSONField, Q, QuerySet
from django.db.models.fields import CharField, TextField
from django.forms.forms import BaseForm
from django.forms.models import ModelForm, ModelFormMetaclass, fields_for_model
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.urls.resolvers import RoutePattern
from django.utils import timezone
from django.utils.functional import classproperty, lazy
from django.utils.translation import gettext as _
from django.views.generic import CreateView, UpdateView
from django.views.generic.edit import DeleteView, ModelFormMixin

import qrcode
import reversion
from dynamic_preferences.settings import preferences_settings
from dynamic_preferences.types import FilePreference
from guardian.admin import GuardedModelAdmin
from guardian.core import ObjectPermissionChecker
from icalendar import Calendar
from material.base import Fieldset, Layout, LayoutNode
from polymorphic.base import PolymorphicModelBase
from polymorphic.models import PolymorphicModel
from ppf.datamatrix import DataMatrix
from qrcode.image.svg import SvgPathFillImage
from rules.contrib.admin import ObjectPermissionsModelAdmin

from aleksis.core.managers import (
    AlekSISBaseManager,
    AlekSISBaseManagerWithoutMigrations,
    PolymorphicBaseManager,
    SchoolTermRelatedQuerySet,
)

from .util.core_helpers import EXTENDED_ITEM_ELEMENT_FIELD_MAP, ExtendedICal20Feed

if TYPE_CHECKING:
    from .models import Group, Person


class _ExtensibleModelBase(models.base.ModelBase):
    """Ensure predefined behaviour on model creation.

    This metaclass serves the following purposes:

     - Register all AlekSIS models with django-reversion
    """

    def __new__(mcls, name, bases, attrs, **kwargs):
        mcls = super().__new__(mcls, name, bases, attrs, **kwargs)

        if not mcls._meta.abstract:
            # Register all non-abstract models with django-reversion
            mcls = reversion.register(mcls)

            mcls.extra_permissions = []

        return mcls


def _generate_one_to_one_proxy_property(field, subfield):
    def getter(self):
        if hasattr(self, field.name):
            related = getattr(self, field.name)
            return getattr(related, subfield.name)
        # Related instane does not exist
        return None

    def setter(self, val):
        if hasattr(self, field.name):
            related = getattr(self, field.name)
        else:
            # Auto-create related instance (but do not save)
            related = field.related_model()
            setattr(related, field.remote_field.name, self)
            # Ensure the related model is saved later
            self._save_reverse = getattr(self, "_save_reverse", []) + [related]
        setattr(related, subfield.name, val)

    return property(getter, setter)


class ExtensibleModel(models.Model, metaclass=_ExtensibleModelBase):
    """Base model for all objects in AlekSIS apps.

    This base model ensures all objects in AlekSIS apps fulfill the
    following properties:

     * `versions` property to retrieve all versions of the model from reversion
     * Allow injection of fields and code from AlekSIS apps to extend
       model functionality.

    Injection of fields and code
    ============================

    After all apps have been loaded, the code in the `model_extensions` module
    in every app is executed. All code that shall be injected into a model goes there.

    :Example:

    .. code-block:: python

       from datetime import date, timedelta

       from aleksis.core.models import Person

       @Person.property
       def is_cool(self) -> bool:
           return True

       @Person.property
       def age(self) -> timedelta:
           return self.date_of_birth - date.today()

    For a more advanced example, using features from the ORM, see AlekSIS-App-Chronos
    and AlekSIS-App-Alsijil.

    :Date: 2019-11-07
    :Authors:
        - Dominik George <dominik.george@teckids.org>
    """

    # Defines a material design icon associated with this type of model
    icon_ = "radiobox-blank"

    managed_by_app_label = models.CharField(
        max_length=255,
        verbose_name="App label of app responsible for managing this instance",
        editable=False,
        blank=True,
    )

    uuid = models.UUIDField(
        db_default=models.Func(function="gen_random_uuid"), editable=False, unique=True
    )
    extended_data = JSONField(default=dict, editable=False)

    extra_permissions = []

    objects = AlekSISBaseManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Ensure all functionality of our extensions that needs saving gets it."""
        # For auto-created remote syncable fields
        if hasattr(self, "_save_reverse"):
            for related in self._save_reverse:
                related.save()
            del self._save_reverse

        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Get the URL of a view representing this model instance."""
        return reverse(
            "object_representation_with_uuid",
            args=[self._meta.app_label, self._meta.model_name, self.uuid],
        )

    def get_object_uri(self, request: HttpRequest | None = None) -> str:
        """Get the full, canonical URI identifying this object."""
        if request is None:
            return urljoin(settings.BASE_URL, self.get_absolute_url())
        else:
            return request.build_absolute_uri(self.get_absolute_url())

    def get_object_qr(self, request: HttpRequest | None = None) -> str:
        """Get QR code of this object's cnanonical URI."""
        return qrcode.make(self.get_object_uri(request), image_factory=SvgPathFillImage).to_string(
            encoding="unicode"
        )

    def get_object_datamatrix(self, request: HttpRequest | None = None) -> str:
        """Get Data Matrix of this object's cnanonical URI."""
        return DataMatrix(self.get_object_uri(request)).svg()

    def get_frontend_url(self) -> Optional[str]:
        """Get the URL in the official AlekSIS web app."""
        return None

    @classmethod
    def from_object_uri(cls, uri: str | HttpRequest) -> "ExtensibleModel":
        """Retrieve a model instance from the full, canonical URI."""
        if isinstance(uri, HttpRequest):
            path = uri.path.lstrip("/")
            get_params = uri.GET
        else:
            splits = uri.removeprefix(settings.BASE_URL).lstrip("/").split("?", 1)
            path = splits[0]
            qs = splits[1] if len(splits) > 1 else ""
            get_params = parse_qs(qs)

        obj = None
        if match := RoutePattern("o/<str:app_label>/<str:model>/<uuid:pk>").match(path):
            kwargs = match[2]
            model = apps.get_model(kwargs["app_label"], kwargs["model"])
            obj = model.objects.get(uuid=kwargs["pk"])
        elif match := RoutePattern("o/<str:app_label>/<str:model>/<int:pk>").match(path):
            kwargs = match[2]
            model = apps.get_model(kwargs["app_label"], kwargs["model"])
            obj = model.objects.get(pk=kwargs["pk"])

        if get_params:
            if obj is None and not RoutePattern("o/?$").match(path):
                return None

            authenticators = get_params.get("authenticators", "").split(",")
            if authenticators == [""]:
                authenticators = list(ObjectAuthenticator.registered_objects_dict.keys())

            for authenticator in authenticators:
                authenticator_class = ObjectAuthenticator.get_object_by_name(authenticator)
                if not authenticator_class:
                    continue
                res = authenticator_class().authenticate(uri, obj)
                if res is None:
                    return None
                if res[1] is not None and obj != res[1]:
                    raise BadRequest("Ambiguous objects identified")
                obj = res[1]
                break

        if isinstance(obj, cls):
            return obj

        return None

    @property
    def versions(self) -> list[tuple[str, tuple[Any, Any]]]:
        """Get all versions of this object from django-reversion.

        Includes diffs to previous version.
        """
        versions = reversion.models.Version.objects.get_for_object(self)

        versions_with_changes = []
        for i, version in enumerate(versions):
            diff = {}
            if i > 0:
                prev_version = versions[i - 1]

                try:
                    for k, val in version.field_dict.items():
                        prev_val = prev_version.field_dict.get(k, None)
                        if prev_val != val:
                            diff[k] = (prev_val, val)
                except reversion.models.Version.DoesNotExist:
                    pass

            versions_with_changes.append((version, diff))

        return versions_with_changes

    @classmethod
    def _safe_add(cls, obj: Any, name: Optional[str]) -> None:
        # Decide the name for the attribute
        if name is None:
            prop_name = obj.__name__
        else:
            if name.isidentifier():
                prop_name = name
            else:
                raise ValueError(f"{name} is not a valid name.")

        # Verify that attribute name does not clash with other names in the class
        if hasattr(cls, prop_name):
            raise ValueError(f"{prop_name} already used.")

        # Let Django's model magic add the attribute if we got here
        cls.add_to_class(name, obj)

    @classmethod
    def property_(cls, func: Callable[[], Any], name: Optional[str] = None) -> None:
        """Add the passed callable as a property."""
        cls._safe_add(property(func), name or func.__name__)

    @classmethod
    def method(cls, func: Callable[[], Any], name: Optional[str] = None) -> None:
        """Add the passed callable as a method."""
        cls._safe_add(func, name or func.__name__)

    @classmethod
    def class_method(cls, func: Callable[[], Any], name: Optional[str] = None) -> None:
        """Add the passed callable as a classmethod."""
        cls._safe_add(classmethod(func), name or func.__name__)

    @classmethod
    def get_filter_fields(cls) -> list[str]:
        """Get names of all text-searchable fields of this model."""
        fields = []
        for field in cls.syncable_fields():
            if isinstance(field, (CharField, TextField)):
                fields.append(field.name)
        return fields

    @classmethod
    def syncable_fields(
        cls, recursive: bool = True, exclude_remotes: list = None
    ) -> list[models.Field]:
        """Collect all fields that can be synced on a model.

        If recursive is True, it recurses into related models and generates virtual
        proxy fields to access fields in related models."""
        if not exclude_remotes:
            exclude_remotes = []

        fields = []
        for field in cls._meta.get_fields():
            if field.is_relation and field.one_to_one and recursive:
                if ExtensibleModel not in field.related_model.__mro__:
                    # Related model is not extensible and thus has no syncable fields
                    continue
                if field.related_model in exclude_remotes:
                    # Remote is excluded, probably to avoid recursion
                    continue

                # Recurse into related model to get its fields as well
                for subfield in field.related_model.syncable_fields(
                    recursive, exclude_remotes + [cls]
                ):
                    # generate virtual field names for proxy access
                    name = f"_{field.name}__{subfield.name}"
                    verbose_name = (
                        f"{field.name} ({field.related_model._meta.verbose_name})"
                        " → {subfield.verbose_name}"
                    )

                    if not hasattr(cls, name):
                        # Add proxy properties to handle access to related model
                        setattr(cls, name, _generate_one_to_one_proxy_property(field, subfield))

                    # Generate a fake field class with enough API to detect attribute names
                    fields.append(
                        type(
                            "FakeRelatedProxyField",
                            (),
                            {
                                "name": name,
                                "verbose_name": verbose_name,
                                "to_python": lambda v: subfield.to_python(v),  # noqa: B023
                            },
                        )
                    )
            elif field.editable and not field.auto_created:
                fields.append(field)

        return fields

    @classmethod
    def syncable_fields_choices(cls) -> tuple[tuple[str, str]]:
        """Collect all fields that can be synced on a model."""
        return tuple(
            [(field.name, field.verbose_name or field.name) for field in cls.syncable_fields()]
        )

    @classmethod
    def syncable_fields_choices_lazy(cls) -> Callable[[], tuple[tuple[str, str]]]:
        """Collect all fields that can be synced on a model."""
        return lazy(cls.syncable_fields_choices, tuple)

    @classmethod
    def add_permission(cls, name: str, verbose_name: str):
        """Dynamically add a new permission to a model."""
        cls.extra_permissions.append((name, verbose_name))

    def set_object_permission_checker(self, checker: ObjectPermissionChecker):
        """Annotate a ``ObjectPermissionChecker`` for use with permission system."""
        self._permission_checker = checker


class _ExtensiblePolymorphicModelBase(_ExtensibleModelBase, PolymorphicModelBase):
    """Base class for extensible, polymorphic models."""


class ExtensiblePolymorphicModel(
    ExtensibleModel, PolymorphicModel, metaclass=_ExtensiblePolymorphicModelBase
):
    """Model class for extensible, polymorphic models."""

    objects = PolymorphicBaseManager()

    class Meta:
        abstract = True
        base_manager_name = "objects"


class PureDjangoModel:
    """No-op mixin to mark a model as deliberately not using ExtensibleModel."""

    pass


class GlobalPermissionModel(models.Model):
    """Base model for global permissions.

    This base model ensures that global permissions are not managed."""

    class Meta:
        default_permissions = ()
        abstract = True
        managed = False


class _ExtensibleFormMetaclass(ModelFormMetaclass):
    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)

        # Enforce a default for the base layout for forms that o not specify one
        base_layout = x.layout.elements if hasattr(x, "layout") else []

        x.base_layout = base_layout
        x.layout = Layout(*base_layout)

        return x


class ExtensibleForm(ModelForm, metaclass=_ExtensibleFormMetaclass):
    """Base model for extensible forms.

    This mixin adds functionality which allows
    - apps to add layout nodes to the layout used by django-material

    :Add layout nodes:

    .. code-block:: python

        from material import Fieldset

        from aleksis.core.forms import ExampleForm

        node = Fieldset("field_name")
        ExampleForm.add_node_to_layout(node)

    """

    @classmethod
    def add_node_to_layout(cls, node: Union[LayoutNode, str], add_fields: bool | None = True):
        """Add a node to `layout` attribute.

        :param node: django-material layout node (Fieldset, Row etc.)
        :type node: LayoutNode
        """
        cls.base_layout.append(node)
        cls.layout = Layout(*cls.base_layout)

        if add_fields:
            visit_nodes = [node]
            while visit_nodes:
                current_node = visit_nodes.pop()
                if isinstance(current_node, Fieldset):
                    visit_nodes += node.elements
                else:
                    field_name = (
                        current_node if isinstance(current_node, str) else current_node.field_name
                    )
                    field = fields_for_model(cls._meta.model, [field_name])[field_name]
                    cls._meta.fields.append(field_name)
                    cls.base_fields[field_name] = field
                    setattr(cls, field_name, field)


class BaseModelAdmin(GuardedModelAdmin, ObjectPermissionsModelAdmin):
    """A base class for ModelAdmin combining django-guardian and rules."""

    pass


class SuccessMessageMixin(ModelFormMixin):
    success_message: Optional[str] = None

    def form_valid(self, form: BaseForm) -> HttpResponse:
        if self.success_message:
            messages.success(self.request, self.success_message)
        return super().form_valid(form)


class SuccessNextMixin(RedirectURLMixin):
    redirect_field_name = "next"

    def get_success_url(self) -> str:
        return LoginView.get_redirect_url(self) or super().get_success_url()


class AdvancedCreateView(SuccessMessageMixin, CreateView):
    pass


class AdvancedEditView(SuccessMessageMixin, UpdateView):
    pass


class AdvancedDeleteView(DeleteView):
    """Common confirm view for deleting.

    .. warning ::

        Using this view, objects are deleted permanently after confirming.
        We recommend to include the mixin :class:`reversion.views.RevisionMixin`
        from `django-reversion` to enable soft-delete.
    """

    success_message: Optional[str] = None

    def form_valid(self, form):
        r = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return r


class SchoolTermRelatedExtensibleModel(ExtensibleModel):
    """Add relation to school term."""

    school_term = models.ForeignKey(
        "core.SchoolTerm",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Linked school term"),
        blank=True,
        null=True,
    )

    objects = AlekSISBaseManagerWithoutMigrations.from_queryset(SchoolTermRelatedQuerySet)()

    class Meta:
        abstract = True


class SchoolTermRelatedExtensibleForm(ExtensibleForm):
    """Extensible form for school term related data.

    .. warning::
        This doesn't automatically include the field `school_term` in `fields` or `layout`,
        it just sets an initial value.
    """

    def __init__(self, *args, **kwargs):
        from aleksis.core.models import SchoolTerm  # noqa

        if "instance" not in kwargs:
            kwargs["initial"] = {"school_term": SchoolTerm.current}

        super().__init__(*args, **kwargs)


class PublicFilePreferenceMixin(FilePreference):
    """Uploads a file to the public namespace."""

    upload_path = "public"

    def get_upload_path(self):
        return os.path.join(
            self.upload_path, preferences_settings.FILE_PREFERENCE_UPLOAD_DIR, self.identifier()
        )


class RegistryObject:
    """Generic registry to allow registration of subclasses over all apps."""

    _registry: ClassVar[Optional[dict[str, type["RegistryObject"]]]] = None
    _class_name: ClassVar[str] = ""

    def __init_subclass__(cls, is_registry=False, register=True):
        parent_registry = getattr(cls, "_registry", None)
        cls._is_registry = False

        if parent_registry is None or is_registry:
            cls._registry = {}
            cls._is_registry = True

            if getattr(cls, "_parent_registries", None) is None:
                cls._parent_registries = []

            if parent_registry is not None:
                cls._parent_registries.append(parent_registry)

        elif register:
            if not cls._class_name:
                cls._class_name = cls.__name__
            cls._register()

    @classmethod
    def _register(cls: type["RegistryObject"]):
        if cls._class_name and cls._class_name not in cls._registry:
            cls._registry[cls._class_name] = cls

            for registry in cls._parent_registries:
                registry[cls._class_name] = cls

    @classmethod
    def get_registry_objects(cls) -> dict[str, type["RegistryObject"]]:
        return cls._registry

    @classmethod
    def get_registry_objects_recursive(cls) -> dict[str, type["RegistryObject"]]:
        objs = cls._registry.copy()
        for sub_registry in cls.get_sub_registries().values():
            objs |= sub_registry.get_registry_objects_recursive()
        return objs

    @classmethod
    def get_sub_registries(cls) -> dict[str, type["RegistryObject"]]:
        registries = {}
        for registry in cls.__subclasses__():
            if registry._registry:
                registries[registry._class_name] = registry
        return registries

    @classmethod
    def get_sub_registries_recursive(cls) -> dict[str, type["RegistryObject"]]:
        registries = {}
        for sub_registry in cls.get_sub_registries().values():
            registries |= sub_registry.get_sub_registries()
        return registries

    @classproperty
    def registered_objects_dict(cls) -> dict[str, type["RegistryObject"]]:
        """Get dict of registered objects."""
        return cls.get_registry_objects()

    @classproperty
    def registered_objects_list(cls) -> list[type["RegistryObject"]]:
        """Get list of registered objects."""
        return list(cls.get_registry_objects().values())

    @classmethod
    def get_object_by_name(cls, name: str) -> Optional[type["RegistryObject"]]:
        """Get registered object by name."""
        return cls.registered_objects_dict.get(name)

    @classmethod
    def get_sub_registry_by_name(cls, name: str) -> Optional[type["RegistryObject"]]:
        return cls.get_sub_registries().get(name)


class ObjectAuthenticator(RegistryObject):
    def authenticate(self, uri, obj):
        raise NotImplementedError()


class DAVResource(RegistryObject):
    """Mixin for objects to provide via DAV."""

    _class_name: ClassVar[str] = ""
    dav_verbose_name: ClassVar[str] = ""
    dav_content_type: ClassVar[str] = ""

    dav_ns: ClassVar[dict[str, str]] = {}
    dav_resource_types: ClassVar[list[str]] = []

    # Hint: We do not support dead properties for now
    dav_live_props: ClassVar[list[tuple[str, str]]] = [
        ("DAV:", "displayname"),
        ("DAV:", "resourcetype"),
        ("DAV:", "getcontenttype"),
        ("DAV:", "getcontentlength"),
    ]
    dav_live_prop_methods: ClassVar[dict[tuple[str, str], str]] = {}

    @classmethod
    def get_dav_verbose_name(cls, request: Optional[HttpRequest] = None) -> str:
        """Return the verbose name of the calendar feed."""
        return str(cls.dav_verbose_name)

    @classmethod
    def _register_dav_ns(cls):
        for prefix, url in cls.dav_ns.items():
            ElementTree.register_namespace(prefix, url)
        ElementTree.register_namespace("d", "DAV:")

    @classmethod
    def _add_dav_propnames(cls, prop: ElementTree.SubElement) -> None:
        for ns, propname in cls.dav_live_props:
            ElementTree.SubElement(prop, f"{{{ns}}}{propname}")

    @classmethod
    def get_dav_absolute_url(cls, reference_object, request: HttpRequest) -> str:
        raise NotImplementedError

    @classmethod
    def get_dav_file_content(
        cls,
        request: HttpRequest,
        objects: Optional[Iterable | QuerySet] = None,
        params: Optional[dict[str, any]] = None,
    ) -> str:
        raise NotImplementedError

    @classmethod
    def get_dav_content_type(cls) -> str:
        return cls.dav_content_type

    @classmethod
    def getetag(cls, request: HttpRequest, objects) -> str:
        if len(objects) == 1:
            key = f"{cls._class_name}_{objects[0].pk}_dav_etag"
            if (cached := cache.get(key, None)) is not None:
                return cached

        warnings.warn(
            f"""The class {cls.__name__} does not override the getetag method and uses the slow and potentially unstable default implementation."""  # noqa: E501
        )
        try:
            content = cls.get_dav_file_content(request, objects)
        except NotImplementedError:
            content = b""
        content = cls.get_dav_file_content(request, objects)
        etag = sha256()
        etag.update(content)
        digest = etag.hexdigest()

        if len(objects) == 1:
            cache.set(key, digest, 60 * 60 * 24)
        return digest

    @classmethod
    def value_unique_id(cls, reference_object, request: Optional[HttpRequest] = None) -> str:
        return reference_object.get_object_uri(request)


class ContactMixin(DAVResource, RegistryObject, is_registry=True):
    _class_name: ClassVar[str] = "contact"  # Unique name for the calendar feed
    dav_verbose_name: ClassVar[str] = ""  # Shown name of the feed
    dav_link: ClassVar[str] = ""  # Link for the feed, optional
    dav_description: ClassVar[str] = ""  # Description of the feed, optional
    dav_color: ClassVar[str] = "#222222"  # Color of the feed, optional
    dav_permission_required: ClassVar[str] = ""

    dav_ns = {
        "carddav": "urn:ietf:params:xml:ns:carddav",
    }
    dav_resource_types = ["{urn:ietf:params:xml:ns:carddav}addressbook"]
    dav_content_type = "text/vcard"

    dav_live_props: ClassVar[list[tuple[str, str]]] = [
        ("DAV:", "displayname"),
        ("DAV:", "resourcetype"),
        ("DAV:", "getcontenttype"),
        ("DAV:", "getcontentlength"),
        (dav_ns["carddav"], "addressbook-description"),
    ]

    @classmethod
    def get_dav_absolute_url(cls, reference_object, request: HttpRequest) -> str:
        return reverse(
            "dav_resource_contact", args=["contact", cls._class_name, reference_object.id]
        )

    def _is_unrequested_prop(self, efield, params):
        """Return True if specific fields are requested and efield is not one of those.
        If no fields are specified or efield is requested, return False"""

        comp_name = "VCARD"

        return (
            params is not None
            and comp_name in params
            and efield is not None
            and efield.upper() not in params[comp_name]
        )

    @classmethod
    def get_objects(
        cls,
        request: HttpRequest | None = None,
        start_qs: QuerySet | None = None,
        additional_filter: Q | None = None,
        select_related: Sequence | None = None,
        prefetch_related: Sequence | None = None,
    ) -> QuerySet:
        """Return all objects that should be included in the contact list."""
        qs = cls.objects if start_qs is None else start_qs
        if isinstance(qs, PolymorphicBaseManager):
            qs = qs.instance_of(cls)
        if additional_filter is not None:
            qs = qs.filter(additional_filter)
        if select_related is not None:
            qs = qs.select_related(*select_related)
        if prefetch_related is not None:
            qs = qs.prefetch_related(*prefetch_related)
        return cls.objects.filter(id__in=qs.values_list("id", flat=True))


class CalendarEventMixin(DAVResource, RegistryObject, is_registry=True):
    """Mixin for calendar feeds.

    This mixin can be used to create calendar feeds for objects. It can be used
    by adding it to a model or another object. The basic attributes of the calendar
    can be set by either setting the attributes of the class or by implementing
    the corresponding class methods. Please notice that the class methods are
    overriding the attributes. The following attributes are mandatory:

    - name: Unique name for the calendar feed
    - verbose_name: Shown name of the feed

    The respective class methods have a `get_` prefix and are called without any arguments.
    There are also some more attributes. Please refer to the class signature for more
    information.

    The list of objects used to create the calendar feed have to be provided by
    the method `get_objects` class method. It's mandatory to implement this method.

    The list of objects whose respective events should be marked as being relevant to the
    availability of the respective entities passed to it (persons, groups, ...) have to be
    provided by the `get_availability_objects` class method. If the method is not implemented,
    no objects will be marked.

    To provide the data for the events, a certain set of class methods can be implemented.
    The following iCal attributes are supported:

    guid, title, description, link, class, created, updateddate, start_datetime, end_datetime,
    location, geolocation, transparency, organizer, attendee, rrule, rdate, exdate, valarm, status

    Additionally, the color attribute is supported. The color has to be an RGB
    color in the format #ffffff.

    To deploy extra meta data for AlekSIS' own calendar frontend, you can add a
    dictionary for the meta attribute.

    To implement a method for a certain attribute, the name of the method has to be
    `value_<your_attribute>`. For example, to implement the `title` attribute, the
    method `value_title` has to be implemented. The method has to return the value
    for the attribute. The method is called with the reference object as argument.
    """

    _class_name: ClassVar[str] = "calendar"  # Unique name for the calendar feed
    dav_verbose_name: ClassVar[str] = ""  # Shown name of the feed
    dav_link: ClassVar[str] = ""  # Link for the feed, optional
    dav_description: ClassVar[str] = ""  # Description of the feed, optional
    dav_color: ClassVar[str] = "#222222"  # Color of the feed, optional
    dav_permission_required: ClassVar[str] = ""

    show_in_overview: bool = True  # Indicates whether the feed is shown in the calendar overview

    dav_ns = {
        "cal": "urn:ietf:params:xml:ns:caldav",
        "ical": "http://apple.com/ns/ical/",
    }
    dav_resource_types = ["{urn:ietf:params:xml:ns:caldav}calendar"]
    dav_content_type = "text/calendar; charset=utf8; component=vevent"

    dav_live_props: ClassVar[list[tuple[str, str]]] = [
        ("DAV:", "displayname"),
        ("DAV:", "resourcetype"),
        ("DAV:", "getcontenttype"),
        ("DAV:", "getcontentlength"),
        (dav_ns["ical"], "calendar-color"),
        (dav_ns["cal"], "calendar-description"),
    ]

    @classmethod
    def get_verbose_name(cls, request: Optional[HttpRequest] = None) -> str:
        """Return the verbose name of the calendar feed."""
        return cls.dav_verbose_name

    @classmethod
    def get_link(cls, request: Optional[HttpRequest] = None) -> str:
        """Return the link of the calendar feed."""
        return cls.dav_link

    @classmethod
    def get_description(cls, request: Optional[HttpRequest] = None) -> str:
        """Return the description of the calendar feed."""
        return cls.dav_description

    @classmethod
    def get_language(cls, request: Optional[HttpRequest] = None) -> str:
        """Return the language of the calendar feed."""
        if request:
            return request.LANGUAGE_CODE
        return settings.LANGUAGE_CODE

    @classmethod
    def get_color(cls, request: Optional[HttpRequest] = None) -> str:
        """Return the color of the calendar feed.

        The color has to be an RGB color in the format #ffffff.
        """
        return cls.dav_color

    @classmethod
    def get_enabled(cls, request: HttpRequest | None = None) -> bool:
        """Return whether the calendar is visible in the frontend."""
        if cls.dav_permission_required and request:
            return request.user.has_perm(cls.dav_permission_required)
        return True

    @classmethod
    def create_event(
        cls,
        reference_object: Any,
        feed: ExtendedICal20Feed,
        request: Optional[HttpRequest] = None,
        params: Optional[dict[str, any]] = None,
    ) -> dict[str, Any]:
        """Create an event for the given reference object and add it to the feed."""
        values = {}
        values["timestamp"] = timezone.now()
        values["description"] = None
        values["component_type"] = cls.get_event_field_value(
            reference_object, "component_type", request=request, params=params
        )
        for field in cls.get_event_field_names():
            field_value = cls.get_event_field_value(
                reference_object, field, request=request, params=params
            )
            if field_value is not None:
                values[field] = field_value
        feed.add_item(**values)
        return values

    @classmethod
    def start_feed(
        cls, request: Optional[HttpRequest] = None, params: Optional[dict[str, any]] = None
    ) -> ExtendedICal20Feed:
        """Start the feed and return it."""
        feed = ExtendedICal20Feed(
            title=cls.get_verbose_name(request=request),
            link=cls.get_link(request=request),
            description=cls.get_description(request=request),
            language=cls.get_language(request=request),
            color=cls.get_color(request=request),
        )
        return feed

    @classmethod
    def get_objects(
        cls,
        request: HttpRequest | None = None,
        params: dict[str, any] | None = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        start_qs: QuerySet | None = None,
        additional_filter: Q | None = None,
        select_related: Sequence | None = None,
        prefetch_related: Sequence | None = None,
        expand_start: Optional[datetime] = None,
        expand_end: Optional[datetime] = None,
        expand: bool = False,
    ) -> QuerySet:
        """Return all objects that should be included in the calendar."""
        qs = cls.objects if start_qs is None else start_qs
        if isinstance(qs, PolymorphicBaseManager):
            qs = qs.instance_of(cls)
        if not start or not end:
            if additional_filter is not None:
                qs = qs.filter(additional_filter)
            if select_related is not None:
                qs = qs.select_related(*select_related)
            if prefetch_related is not None:
                qs = qs.prefetch_related(*prefetch_related)
        else:
            qs = cls.objects.with_occurrences(
                start,
                end,
                start_qs=qs,
                additional_filter=additional_filter,
                select_related=select_related,
                prefetch_related=prefetch_related,
                expand_start=expand_start,
                expand_end=expand_end,
                expand=expand,
            )
        return qs

    @classmethod
    def get_availability_objects(
        cls,
        start: datetime,
        end: datetime,
        request: HttpRequest | None = None,
        expand: bool | None = False,
        obj: Union["Person", "Group"] = None,
    ) -> Iterable:
        """Return the objects whose events should be marked as blocking."""
        return None

    @classmethod
    def create_feed(
        cls,
        request: Optional[HttpRequest] = None,
        params: Optional[dict[str, any]] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        queryset: Optional[QuerySet] = None,
        expand: bool | None = False,
        **kwargs,
    ) -> ExtendedICal20Feed:
        """Create the calendar feed with all events."""
        feed = cls.start_feed(request=request, params=params)

        if queryset is not None:
            reference_queryset = queryset
        else:
            reference_queryset = cls.get_objects(
                request=request, params=params, start=start, end=end, expand=expand, **kwargs
            )

        for reference_object in reference_queryset:
            cls.create_event(reference_object, feed, request=request, params=params)

        return feed

    @classmethod
    def get_calendar_object(
        cls,
        request: Optional[HttpRequest] = None,
        params: Optional[dict[str, any]] = None,
        queryset: Optional[QuerySet] = None,
        expand: bool | None = False,
    ) -> Calendar:
        """Return the calendar object."""
        feed = cls.create_feed(request=request, params=params, queryset=queryset, expand=expand)
        return feed.get_calendar_object(params=params)

    @classmethod
    def get_events(
        cls,
        start: datetime | None = None,
        end: datetime | None = None,
        request: HttpRequest | None = None,
        params: dict[str, any] | None = None,
        with_reference_object: bool = False,
        queryset: Optional[QuerySet] = None,
        expand: bool | None = False,
        **kwargs,
    ) -> Calendar:
        """Get events for this calendar feed."""

        feed = cls.create_feed(
            request=request,
            params=params,
            start=start,
            end=end,
            queryset=queryset,
            expand=expand,
            **kwargs,
        )
        calendar_object = feed.get_calendar_object(
            with_reference_object=with_reference_object, params=params
        )
        return [
            *calendar_object.walk("VEVENT"),
            *calendar_object.walk("VTODO"),
            *calendar_object.walk("VFREEBUSY"),
        ]

    @classmethod
    def get_single_events(
        cls,
        start: datetime | None = None,
        end: datetime | None = None,
        request: HttpRequest | None = None,
        params: dict[str, any] | None = None,
        with_reference_object: bool = False,
        queryset: Optional[QuerySet] = None,
        expand: bool | None = True,
        **kwargs,
    ):
        """Get single events for this calendar feed."""
        return cls.get_events(
            start=start,
            end=end,
            request=request,
            params=params,
            with_reference_object=with_reference_object,
            queryset=queryset,
            expand=expand,
            **kwargs,
        )

    @classmethod
    def get_event_field_names(cls) -> list[str]:
        """Return the names of the fields to be used for the feed."""
        return [field_map[0] for field_map in EXTENDED_ITEM_ELEMENT_FIELD_MAP]

    @classmethod
    def get_event_field_value(
        cls,
        reference_object,
        field_name: str,
        request: HttpRequest | None = None,
        params: dict[str, Any] | None = None,
    ) -> any:
        """Return the value for the given field name."""
        method_name = f"value_{field_name}"
        if hasattr(cls, method_name) and callable(getattr(cls, method_name)):
            return getattr(cls, method_name)(reference_object, request=request)
        return None

    @classmethod
    def value_link(cls, reference_object, request: HttpRequest | None = None) -> str:
        return ""

    @classmethod
    def value_color(cls, reference_object, request: HttpRequest | None = None) -> str:
        return cls.get_color(request=request)

    @classmethod
    def value_component_type(cls, reference_object, request: HttpRequest | None = None):
        return "event"

    @classproperty
    def valid_feed(cls) -> bool:
        """Return if the feed is valid."""
        return cls._class_name != cls.__name__

    @classproperty
    def valid_feeds(cls):
        """Return a list of valid feeds."""
        return [feed for feed in cls.registered_objects_list if feed.valid_feed]

    @classproperty
    def valid_feed_names(cls) -> list[str]:
        """Return a list of valid feed names."""
        return [feed._class_name for feed in cls.valid_feeds]

    @classmethod
    def get_object_by_name(cls, name):
        return cls.registered_objects_dict.get(name)

    @classmethod
    def get_activated(cls, person: "Person") -> bool:
        return cls._class_name in person.preferences["calendar__activated_calendars"]

    @classmethod
    def get_enabled_feeds(cls, request: HttpRequest | None = None):
        return [feed for feed in cls.valid_feeds if feed.get_enabled(request)]

    @classmethod
    def get_overview_feeds(cls, request: HttpRequest | None = None):
        return [feed for feed in cls.get_enabled_feeds(request) if feed.show_in_overview]

    @classmethod
    def get_dav_verbose_name(cls, request: Optional[HttpRequest] = None) -> str:
        return str(cls.get_verbose_name())

    @classmethod
    def get_dav_file_content(
        cls,
        request: HttpRequest,
        objects: Optional[Iterable | QuerySet] = None,
        params: Optional[dict[str, any]] = None,
        expand_start: datetime | None = None,
        expand_end: datetime | None = None,
    ):
        feed = cls.create_feed(request, queryset=objects, params=params)
        return feed.to_ical(params=params)

    @classmethod
    def get_dav_absolute_url(cls, reference_object, request: HttpRequest) -> str:
        return reverse(
            "dav_resource_calendar", args=["calendar", cls._class_name, reference_object.id]
        )
