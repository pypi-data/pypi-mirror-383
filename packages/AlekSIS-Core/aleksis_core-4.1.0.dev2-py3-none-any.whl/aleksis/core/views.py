from textwrap import wrap
from typing import Any, ClassVar, Optional
from urllib.parse import urlencode, urlparse, urlunparse
from uuid import UUID
from xml.etree import ElementTree
from xml.sax import SAXParseException

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.models import Permission, User
from django.contrib.auth.views import LogoutView
from django.core.exceptions import BadRequest, ObjectDoesNotExist, PermissionDenied, ValidationError
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    HttpResponseServerError,
    JsonResponse,
    QueryDict,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.defaults import ERROR_500_TEMPLATE_NAME
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import DeleteView, FormView

import rest_framework
import reversion
from allauth.account.views import LoginView as AllAuthLoginView
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialAccount
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, SingleTableView
from dynamic_preferences.forms import preference_form_builder
from graphene.validation import depth_limit_validator
from graphene_file_upload.django import FileUploadGraphQLView
from graphql import (
    ExecutionResult,
    GraphQLError,
    parse,
    validate,
)
from guardian.shortcuts import GroupObjectPermission, UserObjectPermission
from haystack.generic_views import SearchView
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from haystack.utils.loading import UnifiedIndex
from health_check.views import MainView
from invitations.views import SendInvite
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.exceptions import OAuthToolkitError
from oauth2_provider.models import get_application_model
from oauth2_provider.views import AuthorizationView
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.request import Request as APIRequest
from rest_framework.response import Response as APIResponse
from rest_framework.views import APIView
from reversion import set_user
from rules.contrib.views import PermissionRequiredMixin, permission_required

from .decorators import pwa_cache
from .filters import (
    GroupGlobalPermissionFilter,
    GroupObjectPermissionFilter,
    UserGlobalPermissionFilter,
    UserObjectPermissionFilter,
)
from .forms import (
    AssignPermissionForm,
    EditGroupForm,
    GroupPreferenceForm,
    PersonPreferenceForm,
    SelectPermissionForm,
    SitePreferenceForm,
)
from .mixins import (
    AdvancedDeleteView,
    CalendarEventMixin,
    DAVResource,
    ExtensibleModel,
    ObjectAuthenticator,
    RegistryObject,
    SuccessNextMixin,
)
from .models import (
    Group,
    Person,
    PersonInvitation,
)
from .registries import (
    group_preferences_registry,
    person_preferences_registry,
    site_preferences_registry,
)
from .schema import schema
from .tables import (
    GroupGlobalPermissionTable,
    GroupObjectPermissionTable,
    InvitationsTable,
    UserGlobalPermissionTable,
    UserObjectPermissionTable,
)
from .util import messages
from .util.auth_helpers import BasicAuthMixin
from .util.core_helpers import (
    generate_random_code,
    get_allowed_object_ids,
    get_pwa_icons,
    get_site_preferences,
    has_person,
    objectgetter_optional,
)
from .util.dav_handler.base import DAVMultistatus, DAVRequest
from .util.forms import PreferenceLayout
from .util.pdf import render_pdf

if settings.SENTRY_ENABLED:
    import sentry_sdk


class LogoView(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        image = get_site_preferences()["theme__logo"]
        image_url = image.url if image else static("img/aleksis-banner.svg")

        return redirect(image_url)


class RenderPDFView(TemplateView):
    """View to render a PDF file from a template.

    Makes use of ``render_pdf``.
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = self.get_context_data(**kwargs)
        return render_pdf(request, self.template_name, context)


class ServiceWorkerView(View):
    """Render serviceworker.js under root URL.

    This can't be done by static files,
    because the PWA has a scope and
    only accepts service worker files from the root URL.
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        with open(settings.SERVICE_WORKER_PATH) as f:
            return HttpResponse(f, content_type="application/javascript")


class ManifestView(View):
    """Build manifest.json for PWA."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        prefs = get_site_preferences()
        pwa_imgs = get_pwa_icons()

        icons = [
            {
                "src": favicon_img.faviconImage.url,
                "sizes": f"{favicon_img.size}x{favicon_img.size}",
                "purpose": "any maskable" if prefs["theme__pwa_icon_maskable"] else "any",
            }
            for favicon_img in pwa_imgs
        ]

        manifest = {
            "name": prefs["general__title"],
            "short_name": prefs["general__title"],
            "description": prefs["general__description"],
            "start_url": "/",
            "scope": "/",
            "lang": get_language(),
            "display": "standalone",
            "orientation": "any",
            "status_bar": "default",
            "background_color": "#ffffff",
            "theme_color": prefs["theme__primary"],
            "icons": icons,
        }
        return JsonResponse(manifest)


@method_decorator(pwa_cache, name="dispatch")
class OfflineView(TemplateView):
    """Show an error page if there is no internet connection."""

    template_name = "offline.html"


def get_group_by_id(request: HttpRequest, id_: Optional[int] = None):
    if id_:
        return get_object_or_404(Group, id=id_)
    else:
        return None


@never_cache
@permission_required("core.edit_group_rule", fn=objectgetter_optional(Group, None, False))
def edit_group(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    """View to edit or create a group."""
    context = {}

    group = objectgetter_optional(Group, None, False)(request, id_)
    context["group"] = group

    if id_:
        # Edit form for existing group
        edit_group_form = EditGroupForm(request.POST or None, request.FILES or None, instance=group)
    else:
        # Empty form to create a new group
        if request.user.has_perm("core.create_group_rule"):
            edit_group_form = EditGroupForm(request.POST or None, request.FILES or None)
        else:
            raise PermissionDenied()

    if edit_group_form.is_valid():
        with reversion.create_revision():
            set_user(request.user)
            group = edit_group_form.save(commit=True)

        messages.success(request, _("The group has been saved."))

        return redirect("group_by_id", group.pk)

    context["edit_group_form"] = edit_group_form

    return render(request, "core/group/edit.html", context)


class SystemStatusAPIView(PermissionRequiredMixin, MainView):
    """Provide information about system status as JSON."""

    permission_required = "core.view_system_status_rule"

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        status_code = 500 if self.errors else 200

        return self.render_to_response_json(self.plugins, status_code)


class TestPDFGenerationView(PermissionRequiredMixin, RenderPDFView):
    template_name = "core/pages/test_pdf.html"
    permission_required = "core.test_pdf_rule"


@permission_required("core.search_rule")
def searchbar_snippets(request: HttpRequest) -> HttpResponse:
    """View to return HTML snippet with searchbar autocompletion results."""
    query = request.GET.get("q", "")
    limit = int(request.GET.get("limit", "5"))
    indexed_models = UnifiedIndex().get_indexed_models()
    allowed_object_ids = get_allowed_object_ids(request, indexed_models)
    results = (
        SearchQuerySet().filter(id__in=allowed_object_ids).filter(text=AutoQuery(query))[:limit]
    )
    context = {"results": results}

    return render(request, "search/searchbar_snippets.html", context)


@method_decorator(pwa_cache, name="dispatch")
class PermissionSearchView(PermissionRequiredMixin, SearchView):
    """Wrapper to apply permission to haystack's search view."""

    permission_required = "core.search_rule"

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        indexed_models = UnifiedIndex().get_indexed_models()
        allowed_object_ids = get_allowed_object_ids(self.request, indexed_models)
        queryset = queryset.filter(id__in=allowed_object_ids)

        return super().get_context_data(object_list=queryset, **kwargs)


@never_cache
def preferences(
    request: HttpRequest,
    registry_name: str = "person",
    pk: Optional[int] = None,
    section: Optional[str] = None,
) -> HttpResponse:
    """View for changing preferences."""
    context = {}

    # Decide which registry to use and check preferences
    if registry_name == "site":
        registry = site_preferences_registry
        instance = None
        form_class = SitePreferenceForm

        if not request.user.has_perm("core.change_site_preferences_rule", instance):
            raise PermissionDenied()
    elif registry_name == "person":
        registry = person_preferences_registry
        instance = objectgetter_optional(Person, "request.user.person", True)(request, pk)
        form_class = PersonPreferenceForm

        if not request.user.has_perm("core.change_person_preferences_rule", instance):
            raise PermissionDenied()
    elif registry_name == "group":
        registry = group_preferences_registry
        instance = objectgetter_optional(Group, None, False)(request, pk)
        form_class = GroupPreferenceForm

        if not request.user.has_perm("core.change_group_preferences_rule", instance):
            raise PermissionDenied()
    else:
        # Invalid registry name passed from URL
        raise Http404(_("The requested preference registry does not exist"))

    if not section and len(registry.sections()) > 0:
        default_section = list(registry.sections())[0]
        if instance:
            return redirect(f"preferences_{registry_name}", instance.pk, default_section)
        else:
            return redirect(f"preferences_{registry_name}", default_section)

    # Build final form from dynamic-preferences
    form_class = preference_form_builder(form_class, instance=instance, section=section)

    # Get layout
    form_class.layout = PreferenceLayout(form_class, section=section)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES or None)
        if form.is_valid():
            form.update_preferences()
            messages.success(request, _("The preferences have been saved successfully."))
    else:
        form = form_class()

    context["registry"] = registry
    context["registry_name"] = registry_name
    context["section"] = section
    context["registry_url"] = "preferences_" + registry_name
    context["form"] = form
    context["instance"] = instance

    return render(request, "dynamic_preferences/form.html", context)


@permission_required("core.delete_group_rule", fn=objectgetter_optional(Group))
def delete_group(request: HttpRequest, id_: int) -> HttpResponse:
    """View to delete an group."""
    group = objectgetter_optional(Group)(request, id_)
    with reversion.create_revision():
        set_user(request.user)
        group.save()

    group.delete()
    messages.success(request, _("The group has been deleted."))

    return redirect("groups")


class InvitePerson(PermissionRequiredMixin, SingleTableView, SendInvite):
    """View to invite a person to register an account."""

    template_name = "invitations/forms/_invite.html"
    permission_required = "core.invite_rule"
    model = PersonInvitation
    table_class = InvitationsTable
    context = {}

    def dispatch(self, request, *args, **kwargs):
        if not get_site_preferences()["auth__invite_enabled"]:
            return HttpResponseRedirect(reverse_lazy("invite_disabled"))
        return super().dispatch(request, *args, **kwargs)

    # Get queryset of invitations
    def get_context_data(self, **kwargs):
        queryset = kwargs.pop("object_list", None)
        if queryset is None:
            self.object_list = self.model.objects.all()
        return super().get_context_data(**kwargs)


class GenerateInvitationCode(View):
    """View to generate an invitation code."""

    def get(self, request):
        # Build code
        length = get_site_preferences()["auth__invite_code_length"]
        packet_size = get_site_preferences()["auth__invite_code_packet_size"]
        code = generate_random_code(length, packet_size)

        # Create invitation object
        invitation = PersonInvitation.objects.create(
            email="", inviter=request.user, key=code, sent=timezone.now()
        )

        # Make code more readable
        code = "-".join(wrap(invitation.key, 5))

        # Generate success message and print code
        messages.success(
            request,
            _(f"The invitation was successfully created. The invitation code is {code}"),
        )

        return redirect("invite_person")


@method_decorator(pwa_cache, name="dispatch")
class PermissionsListBaseView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    """Base view for list of all permissions."""

    template_name = "core/perms/list.html"
    permission_required = "core.manage_permissions_rule"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assign_form"] = SelectPermissionForm()
        context["tab"] = self.tab

        return context


@method_decorator(pwa_cache, name="dispatch")
class UserGlobalPermissionsListBaseView(PermissionsListBaseView):
    """List all global user permissions."""

    filterset_class = UserGlobalPermissionFilter
    table_class = UserGlobalPermissionTable
    tab = "user_global"


@method_decorator(pwa_cache, name="dispatch")
class GroupGlobalPermissionsListBaseView(PermissionsListBaseView):
    """List all global group permissions."""

    filterset_class = GroupGlobalPermissionFilter
    table_class = GroupGlobalPermissionTable
    tab = "group_global"


@method_decorator(pwa_cache, name="dispatch")
class UserObjectPermissionsListBaseView(PermissionsListBaseView):
    """List all object user permissions."""

    filterset_class = UserObjectPermissionFilter
    table_class = UserObjectPermissionTable
    tab = "user_object"


@method_decorator(pwa_cache, name="dispatch")
class GroupObjectPermissionsListBaseView(PermissionsListBaseView):
    """List all object group permissions."""

    filterset_class = GroupObjectPermissionFilter
    table_class = GroupObjectPermissionTable
    tab = "group_object"


@method_decorator(pwa_cache, name="dispatch")
class SelectPermissionForAssignView(PermissionRequiredMixin, FormView):
    """View for selecting a permission to assign."""

    permission_required = "core.manage_permissions_rule"
    form_class = SelectPermissionForm

    def form_valid(self, form: SelectPermissionForm) -> HttpResponse:
        url = reverse("assign_permission", args=[form.cleaned_data["selected_permission"].pk])
        params = {"next": self.request.GET["next"]} if "next" in self.request.GET else {}
        return redirect(f"{url}?{urlencode(params)}")

    def form_invalid(self, form: SelectPermissionForm) -> HttpResponse:
        return redirect("manage_group_object_permissions")


class AssignPermissionView(SuccessNextMixin, PermissionRequiredMixin, DetailView, FormView):
    """View for assigning a permission to users/groups for all/some objects."""

    permission_required = "core.manage_permissions"
    queryset = Permission.objects.all()
    template_name = "core/perms/assign.html"
    form_class = AssignPermissionForm
    success_url = "manage_user_global_permissions"

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["permission"] = self.get_object()
        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        # Overwrite get_context_data to ensure correct function call order
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form: AssignPermissionForm) -> HttpResponse:
        form.save_perms()
        messages.success(
            self.request,
            _("We have successfully assigned the permissions."),
        )
        return redirect(self.get_success_url())


class UserGlobalPermissionDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete a global user permission."""

    permission_required = "core.manage_permissions"
    model = User.user_permissions.through
    success_message = _("The global user permission has been deleted.")
    success_url = reverse_lazy("manage_user_global_permissions")
    template_name = "core/pages/delete.html"


class GroupGlobalPermissionDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete a global group permission."""

    permission_required = "core.manage_permissions"
    model = DjangoGroup.permissions.through
    success_message = _("The global group permission has been deleted.")
    success_url = reverse_lazy("manage_group_global_permissions")
    template_name = "core/pages/delete.html"


class UserObjectPermissionDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete a object user permission."""

    permission_required = "core.manage_permissions"
    model = UserObjectPermission
    success_message = _("The object user permission has been deleted.")
    success_url = reverse_lazy("manage_user_object_permissions")
    template_name = "core/pages/delete.html"


class GroupObjectPermissionDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete a object group permission."""

    permission_required = "core.manage_permissions"
    model = GroupObjectPermission
    success_message = _("The object group permission has been deleted.")
    success_url = reverse_lazy("manage_group_object_permissions")
    template_name = "core/pages/delete.html"


class SocialAccountDeleteView(DeleteView):
    """Custom view to delete django-allauth social account."""

    template_name = "core/pages/delete.html"
    success_url = reverse_lazy("socialaccount_connections")

    def get_queryset(self):
        return SocialAccount.objects.filter(user=self.request.user)

    def form_valid(self, form):
        self.object = self.get_object()
        try:
            get_adapter(self.request).validate_disconnect(
                self.object, SocialAccount.objects.filter(user=self.request.user)
            )
        except ValidationError:
            messages.error(
                self.request,
                _(
                    "The third-party account could not be disconnected "
                    "because it is the only login method available."
                ),
            )
        else:
            self.object.delete()
            messages.success(
                self.request, _("The third-party account has been successfully disconnected.")
            )
        return super().form_valid()


def server_error(
    request: HttpRequest, template_name: str = ERROR_500_TEMPLATE_NAME
) -> HttpResponseServerError:
    """Ensure the request is passed to the error page."""
    template = loader.get_template(template_name)
    context = {"request": request}

    return HttpResponseServerError(template.render(context))


class InvitePersonByID(PermissionRequiredMixin, SingleObjectMixin, View):
    """Custom view to invite person by their ID."""

    model = Person
    success_url = reverse_lazy("persons")
    permission_required = "core.invite_rule"

    def dispatch(self, request, *args, **kwargs):
        if not get_site_preferences()["auth__invite_enabled"]:
            return HttpResponseRedirect(reverse_lazy("invite_disabled"))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        person = self.get_object()

        if not person.email or not PersonInvitation.objects.filter(email=person.email).exists():
            length = get_site_preferences()["auth__invite_code_length"]
            packet_size = get_site_preferences()["auth__invite_code_packet_size"]
            key = generate_random_code(length, packet_size)
            invite = PersonInvitation.objects.create(person=person, key=key)
            if person.email:
                invite.email = person.email
            invite.inviter = self.request.user
            invite.save()

            invite.send_invitation(self.request)

            if person.email:
                messages.success(
                    self.request,
                    _(
                        "Person was invited successfully and an email "
                        "with further instructions has been send to them."
                    ),
                )
            else:
                readable_key = "-".join(wrap(key, packet_size))
                messages.success(
                    self.request,
                    f"{_('Person was invited successfully. Their key is')} {readable_key}.",
                )
        else:
            messages.success(self.request, _("Person was already invited."))

        return redirect("person_by_id", person.pk)


class InviteDisabledView(PermissionRequiredMixin, TemplateView):
    """View to display a notice that the invite feature is disabled and how to enable it."""

    template_name = "invitations/disabled.html"
    permission_required = "core.change_site_preferences_rule"

    def dispatch(self, request, *args, **kwargs):
        if get_site_preferences()["auth__invite_enabled"]:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class LoginView(AllAuthLoginView):
    """Custom login view."""

    def get_context_data(self, **kwargs):
        """Override context data to hide side menu and include OAuth2 application if given."""
        context = super().get_context_data(**kwargs)
        if self.request.GET.get("oauth") and self.request.GET.get("client_id"):
            application = get_application_model().objects.get(
                client_id=self.request.GET["client_id"]
            )
            context["oauth_application"] = application
        return context


class CustomAuthorizationView(AuthorizationView):
    def handle_no_permission(self):
        """Override handle_no_permission to provide OAuth2 information to login page."""
        redirect_obj = super().handle_no_permission()

        try:
            scopes, credentials = self.validate_authorization_request(self.request)
        except OAuthToolkitError as error:
            # Application is not available at this time.
            return self.error_response(error, application=None)

        login_url_parts = list(urlparse(redirect_obj.url))
        querystring = QueryDict(login_url_parts[4], mutable=True)
        querystring["oauth"] = "yes"
        querystring["client_id"] = credentials["client_id"]
        login_url_parts[4] = querystring.urlencode(safe="/")

        return HttpResponseRedirect(urlunparse(login_url_parts))

    def get_context_data(self, **kwargs):
        """Override context data to hide side menu."""
        context = super().get_context_data(**kwargs)
        context["no_menu"] = True
        return context


class LoggingGraphQLView(FileUploadGraphQLView):
    """GraphQL view that raises unknown exceptions instead of blindly catching them."""

    def execute_graphql_request(
        self, request, data, query, variables, operation_name, show_graphiql=False
    ):
        if settings.SENTRY_ENABLED and operation_name:
            scope = sentry_sdk.get_current_scope()
            scope.set_transaction_name(operation_name)

        validation_errors = []

        if query:
            validation_errors = validate(
                schema=schema.graphql_schema,
                document_ast=parse(query),
                rules=(depth_limit_validator(max_depth=10),),
            )
        if validation_errors:
            result = ExecutionResult(data=None, errors=validation_errors)
        else:
            result = super().execute_graphql_request(
                request, data, query, variables, operation_name, show_graphiql
            )

        errors = result.errors or []
        for error in errors:
            if not isinstance(
                error.original_error,
                (GraphQLError, ValidationError, PermissionDenied, ObjectDoesNotExist),
            ):
                if isinstance(error.original_error, ObjectDoesNotExist):
                    raise GraphQLError from PermissionDenied
                raise error

            # Pass validation errors to frontend
            if isinstance(error.original_error, ValidationError):
                error.message = (
                    error.original_error.message_dict
                    if getattr(error.original_error, "error_dict", None)
                    else error.original_error.messages
                )

        return result


class ObjectAuthentication(rest_framework.authentication.BaseAuthentication):
    def authenticate(self, request: APIRequest):
        authenticators = request.GET.get("authenticators", "").split(",")
        if authenticators == [""]:
            authenticators = list(ObjectAuthenticator.registered_objects_dict.keys())

        for authenticator in authenticators:
            authenticator_class = ObjectAuthenticator.get_object_by_name(authenticator)
            if not authenticator_class:
                continue
            res = authenticator_class().authenticate(request, request._aleksis_object)
            if res is None:
                return None
            user, obj = res
            if request._aleksis_object is not None and obj != request._aleksis_object:
                raise BadRequest("Ambiguous objects identified")
            if request._aleksis_object is None:
                request._aleksis_object = obj
            if user is None:
                return None
            return user, obj

        return None


class ObjectSerializer(rest_framework.serializers.BaseSerializer):
    def to_representation(self, instance):
        if hasattr(instance, "get_json"):
            res = instance.get_json(self._context["request"])
        else:
            res = {"id": instance.id}
        res["_meta"] = {
            "model": instance._meta.model_name,
            "app": instance._meta.app_label,
        }

        return res


class ObjectRepresentationView(APIView):
    """View with unique URL to get a JSON representation of an object."""

    authentication_classes = [
        ObjectAuthentication,
        rest_framework.authentication.BasicAuthentication,
        OAuth2Authentication,
        rest_framework.authentication.SessionAuthentication,
    ]
    permission_classes = []
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get_model(self, request: APIRequest, app_label: str, model: str):
        """Get the model by app label and model name."""
        try:
            model = apps.get_model(app_label, model)
            if ExtensibleModel in model.__mro__:
                return model
            else:
                raise Http404
        except LookupError as exc:
            raise Http404 from exc

    def get_object(self, request: APIRequest, app_label: str, model: str, pk: int | UUID):
        """Get the object by app label, model name and primary key."""
        if getattr(self, "model", None) is None:
            self.model = self.get_model(request, app_label, model)

        try:
            if isinstance(pk, UUID):
                return self.model.objects.get(uuid=pk)
            else:
                return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist as exc:
            raise Http404 from exc

    def initial(
        self,
        request: APIRequest,
        app_label: Optional[str] = None,
        model: Optional[str] = None,
        pk: Optional[int | UUID] = None,
        *args,
        **kwargs,
    ):
        if app_label and model:
            request._aleksis_model = self.get_model(request, app_label, model)
        else:
            request._aleksis_model = None

        if app_label and model and pk:
            request._aleksis_object = self.get_object(request, app_label, model, pk)
        else:
            request._aleksis_object = None

        request._aleksis_orig_object = request._aleksis_object
        return super().initial(request, *args, **kwargs)

    def get(
        self,
        request: APIRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        headers = {}
        status = 200
        template_name = None

        if request._aleksis_object is None:
            if has_person(request.user):
                target = request.user.person.get_object_uri()
                if qs := request.GET.urlencode():
                    target += f"?{qs}"
                return HttpResponseRedirect(target)
        elif request._aleksis_object != request._aleksis_orig_object:
            target = request._aleksis_object.get_object_uri()
            if qs := request.GET.urlencode():
                target += f"?{qs}"
            return HttpResponseRedirect(target)

        if isinstance(request.accepted_renderer, TemplateHTMLRenderer):
            if settings.OBJECT_REPR_USE_FRONTEND:
                return APIResponse(None, template_name="core/vue_index.html")
            elif request._aleksis_object is None:
                raise Http404
            else:
                if hasattr(request._aleksis_object, "get_template"):
                    template_name = request._aleksis_object.get_template()
                else:
                    template_name = "core/406.html"
                    status = 406

        if request.user.is_authenticated:
            serializer = ObjectSerializer(request._aleksis_object, context={"request": request})
            return APIResponse(
                serializer.data, status=status, headers=headers, template_name=template_name
            )

        raise PermissionDenied()


class RegistryObjectViewMixin:
    """Provide single registry object by its name."""

    registry_object: ClassVar[type[RegistryObject] | RegistryObject] = None

    def get_object(self) -> type[RegistryObject]:
        if not self.registry_object:
            raise NotImplementedError("There is no registry object set.")

        if "name" in self.kwargs and "subregistry" not in self.kwargs:
            return self._get_sub_registry()

        name = self.kwargs.get("name")
        if name is None:
            return self.registry_object
        if name in self.registry_object.registered_objects_dict:
            return self.registry_object.registered_objects_dict[name]
        raise Http404

    def _get_sub_registry(self) -> type[RegistryObject]:
        name = self.kwargs.get("name")
        if name in self.registry_object.get_sub_registries():
            return self.registry_object.get_sub_registry_by_name(name)
        raise Http404


class ICalFeedView(RegistryObjectViewMixin, PermissionRequiredMixin, View):
    """View to generate an iCal feed for a calendar."""

    permission_required = "core.view_calendar_feed_rule"
    registry_object = CalendarEventMixin

    def get(self, request, name, *args, **kwargs):
        calendar = self.get_object()
        feed = calendar.create_feed(request)
        response = HttpResponse(content_type="text/calendar")
        feed.write(response)
        return response


class ICalAllFeedsView(PermissionRequiredMixin, View):
    """View to generate an iCal feed for all calendars."""

    permission_required = "core.view_calendar_feed_rule"

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/calendar")
        for calendar in CalendarEventMixin.get_enabled_feeds(request):
            feed = calendar.create_feed(request)
            feed.write(response)
        return response


@method_decorator(csrf_exempt, name="dispatch")
class DAVResourceView(BasicAuthMixin, PermissionRequiredMixin, RegistryObjectViewMixin, View):
    """View for CalDAV collections."""

    registry_object = DAVResource
    permission_required = "core.view_calendar_feed_rule"

    http_method_names = View.http_method_names + ["propfind", "report"]
    dav_compliance = []

    _dav_request: ClassVar[DAVRequest]

    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)

        res.headers["DAV"] = ", ".join(
            ["1", "3", "calendar-access", "addressbook"] + self.dav_compliance
        )

        return res

    def options(self, request, *args, **kwargs):
        res = super().options(request, *args, **kwargs)
        return res

    def propfind(self, request, *args, **kwargs):
        resource = self.get_object()
        self._dav_request = DAVRequest(request, resource, None)

        try:
            self._dav_request.parse()
        except SAXParseException:
            return HttpResponseBadRequest()

        multistatus = DAVMultistatus(self._dav_request)
        multistatus.process()

        response = HttpResponse(
            ElementTree.tostring(multistatus.xml_element), content_type="text/xml", status=207
        )
        return response

    def report(self, request, *args, **kwargs):
        return self.propfind(request, *args, **kwargs)


class DAVSingleResourceView(DAVResourceView):
    """View for single CalDAV resources."""

    def propfind(self, request, id, *args, **kwargs):  # noqa: A002
        resource = self.get_object()
        try:
            objects = resource.get_objects(request).get(pk=id)
        except resource.DoesNotExist as exc:
            raise Http404 from exc

        self._dav_request = DAVRequest(request, resource, objects)

        try:
            self._dav_request.parse()
        except SAXParseException:
            return HttpResponseBadRequest()

        multistatus = DAVMultistatus(self._dav_request)
        multistatus.process()

        response = HttpResponse(
            ElementTree.tostring(multistatus.xml_element), content_type="text/xml", status=207
        )
        return response

    def get(self, request, name, id, *args, **kwargs):  # noqa: A002
        resource: DAVResource = self.get_object()
        try:
            objs = resource.get_objects(request)
            if isinstance(objs, set):
                obj = next(filter(lambda o: o.pk == id, objs))
            else:
                obj = objs.get(pk=id)
        except resource.DoesNotExist as exc:
            raise Http404 from exc

        response = HttpResponse(content_type=resource.get_dav_content_type())
        response.write(resource.get_dav_file_content(request, objects=[obj]))
        return response


class CustomLogoutView(LogoutView):
    """Custom logout view that allows GET requests."""

    http_method_names = ["post", "get", "options"]

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)


@method_decorator(csrf_exempt, name="dispatch")
class DAVWellKnownView(View):
    http_method_names = View.http_method_names + ["propfind", "report"]

    def get(self, request, *args, **kwargs):
        return redirect("dav_registry")

    def propfind(self, request, *args, **kwargs):
        return redirect("dav_registry")

    def post(self, request, *args, **kwargs):
        return redirect("dav_registry")
