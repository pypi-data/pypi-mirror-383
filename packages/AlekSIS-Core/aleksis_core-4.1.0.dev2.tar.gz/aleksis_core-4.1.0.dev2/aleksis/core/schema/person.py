from typing import Union

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, SuspiciousOperation, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

import graphene
import graphene_django_optimizer
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from invitations.views import accept_invitation

from ..filters import PersonFilter
from ..models import (
    Activity,
    Address,
    AddressType,
    DummyPerson,
    Person,
    PersonGroupThrough,
    PersonInvitation,
    PersonRelationship,
    Role,
)
from ..util.auth_helpers import custom_username_validators
from ..util.core_helpers import get_site_preferences, has_person
from .address import AddressType as GraphQLAddressType
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    BaseObjectType,
    DjangoFilterMixin,
    FieldFileType,
    PermissionsTypeMixin,
)
from .group import PersonGroupThroughType
from .notification import NotificationType


class PersonPreferencesType(graphene.ObjectType):
    theme_design_mode = graphene.String()
    days_of_week = graphene.List(graphene.Int)

    def resolve_theme_design_mode(parent, info, **kwargs):
        return parent["theme__design"]

    @staticmethod
    def resolve_days_of_week(root, info, **kwargs):
        first_day = root["calendar__first_day_of_the_week"]

        if first_day == "default":
            first_day = get_site_preferences()["calendar__first_day_of_the_week"]

        first_day = int(first_day)

        days = list(map(str, range(7)))
        sorted_days = days[first_day:] + days[:first_day]

        return list(map(int, sorted_days))


class PersonRelationshipType(BaseObjectType):
    """GraphQL type for PersonRelationship"""

    class Meta:
        model = PersonRelationship
        fields = [
            "person",
            "of_person",
            "roles",
        ]


class PersonType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = Person
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "additional_name",
            "short_name",
            "addresses",
            "phone_number",
            "mobile_number",
            "email",
            "date_of_birth",
            "place_of_birth",
            "sex",
            "photo",
            "avatar",
            "primary_group",
            "description",
            "owner_of",
            "member_of",
            "related_persons",
            "related_to_persons",
        ]
        filterset_class = PersonFilter

    id = graphene.ID(required=False)

    full_name = graphene.String()
    username = graphene.String()
    userid = graphene.ID()
    photo = graphene.Field(FieldFileType, required=False)
    avatar = graphene.Field(FieldFileType, required=False)
    avatar_url = graphene.String()
    avatar_content_url = graphene.String()
    secondary_image_url = graphene.String(required=False)

    addresses = graphene.List(GraphQLAddressType, required=False)

    phone_number = graphene.String(required=False)
    mobile_number = graphene.String(required=False)
    email = graphene.String(required=False)

    date_of_birth = graphene.String(required=False)
    place_of_birth = graphene.String(required=False)

    notifications = graphene.List(NotificationType)
    unread_notifications_count = graphene.Int(required=False)

    is_dummy = graphene.Boolean()
    preferences = graphene.Field(PersonPreferencesType)

    can_change_person_preferences = graphene.Boolean()
    can_impersonate_person = graphene.Boolean()
    can_invite_person = graphene.Boolean()
    can_change_password = graphene.Boolean()
    can_send_password_reset_request = graphene.Boolean()

    person_relationships = graphene.List(PersonRelationshipType)
    group_relationships = graphene.List(PersonGroupThroughType)

    children = graphene.List(lambda: PersonType)
    guardians = graphene.List(lambda: PersonType)

    def resolve_addresses(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_addresses_rule", root):
            return root.addresses.all()
        return []

    def resolve_phone_number(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_contact_details_rule", root):
            return root.phone_number
        return None

    def resolve_mobile_number(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_contact_details_rule", root):
            return root.mobile_number
        return None

    def resolve_email(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_contact_details_rule", root):
            return root.email or (root.user.email if root.user else None)
        return None

    def resolve_date_of_birth(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_personal_details_rule", root):
            return root.date_of_birth
        return None

    def resolve_place_of_birth(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_personal_details_rule", root):
            return root.place_of_birth
        return None

    def resolve_person_relationships(root, info, **kwargs):  # noqa
        if getattr(root, "can_view_person_groups", False) or info.context.user.has_perm(
            "core.view_personal_details", root
        ):
            return PersonRelationship.objects.filter(Q(person=root) | Q(of_person=root))
        return []

    def resolve_related_persons(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_personal_details_rule", root):
            return root.related_persons.all()
        return []

    def resolve_related_to_persons(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_personal_details_rule", root):
            return root.related_to_persons.all()
        return []

    def resolve_children(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_personal_details_rule", root):
            relationships = PersonRelationship.objects.filter(
                person=root, roles__short_name="guardian"
            )
            return Person.objects.filter(pk__in=relationships.values_list("of_person", flat=True))
        return []

    def resolve_guardians(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_personal_details_rule", root):
            relationships = PersonRelationship.objects.filter(
                of_person=root, roles__short_name="guardian"
            )
            return Person.objects.filter(pk__in=relationships.values_list("person", flat=True))
        return []

    def resolve_group_relationships(root, info, **kwargs):  # noqa
        if getattr(root, "can_view_person_groups", False) or info.context.user.has_perm(
            "core.view_person_groups_rule", root
        ):
            return PersonGroupThrough.objects.filter(person=root)
        return []

    def resolve_member_of(root, info, **kwargs):  # noqa
        if getattr(root, "can_view_person_groups", False) or info.context.user.has_perm(
            "core.view_person_groups_rule", root
        ):
            return root.member_of.all()
        return []

    def resolve_owner_of(root, info, **kwargs):  # noqa
        if getattr(root, "can_view_person_groups", False) or info.context.user.has_perm(
            "core.view_person_groups_rule", root
        ):
            return root.owner_of.all()
        return []

    @graphene_django_optimizer.resolver_hints(
        model_field="user",
    )
    def resolve_username(root, info, **kwargs):  # noqa
        return root.user.username if root.user else None

    @graphene_django_optimizer.resolver_hints(
        model_field="user",
    )
    def resolve_userid(root, info, **kwargs):  # noqa
        return root.user.id if root.user else None

    def resolve_unread_notifications_count(root, info, **kwargs):  # noqa
        if root.pk and has_person(info.context) and root == info.context.user.person:
            return root.unread_notifications_count
        elif root.pk:
            return 0
        return None

    def resolve_photo(root, info, **kwargs):
        if info.context.user.has_perm("core.view_photo_rule", root):
            return root.photo
        return None

    def resolve_avatar(root, info, **kwargs):
        if info.context.user.has_perm("core.view_avatar_rule", root):
            return root.avatar
        return None

    def resolve_avatar_url(root, info, **kwargs):
        if info.context.user.has_perm("core.view_avatar_rule", root) and root.avatar:
            return root.avatar.url
        return root.identicon_url

    def resolve_avatar_content_url(root, info, **kwargs):  # noqa
        # Returns the url for the main image for a person, either the avatar, photo or identicon,
        # based on permissions and preferences
        if get_site_preferences()["account__person_prefer_photo"]:
            if info.context.user.has_perm("core.view_photo_rule", root) and root.photo:
                return root.photo.url
            elif info.context.user.has_perm("core.view_avatar_rule", root) and root.avatar:
                return root.avatar.url

        else:
            if info.context.user.has_perm("core.view_avatar_rule", root) and root.avatar:
                return root.avatar.url
            elif info.context.user.has_perm("core.view_photo_rule", root) and root.photo:
                return root.photo.url

        return root.identicon_url

    def resolve_secondary_image_url(root, info, **kwargs):  # noqa
        # returns either the photo url or the avatar url,
        # depending on the one returned by avatar_content_url

        if get_site_preferences()["account__person_prefer_photo"]:
            if info.context.user.has_perm("core.view_avatar_rule", root) and root.avatar:
                return root.avatar.url
        elif info.context.user.has_perm("core.view_photo_rule", root) and root.photo:
            return root.photo.url
        return None

    def resolve_is_dummy(root: Union[Person, DummyPerson], info, **kwargs):
        return root.is_dummy if hasattr(root, "is_dummy") else False

    def resolve_notifications(root: Person, info, **kwargs):
        if root.pk and has_person(info.context) and root == info.context.user.person:
            return root.notifications.filter(send_at__lte=timezone.now()).order_by(
                "read", "-created"
            )
        return []

    def resolve_can_change_person_preferences(root, info, **kwargs):  # noqa
        return info.context.user.has_perm("core.change_person_preferences_rule", root)

    def resolve_can_impersonate_person(root, info, **kwargs):  # noqa
        return root.user and info.context.user.has_perm("core.impersonate_rule", root)

    def resolve_can_invite_person(root, info, **kwargs):  # noqa
        return (not root.user) and info.context.user.has_perm("core.invite_rule", root)

    @staticmethod
    def resolve_can_edit(root, info, **kwargs):
        if hasattr(root, "can_edit"):
            return root.can_edit
        return info.context.user.has_perm("core.edit_person_rule", root)

    @staticmethod
    def resolve_can_delete(root, info, **kwargs):
        if hasattr(root, "can_delete"):
            return root.can_delete
        return info.context.user.has_perm("core.delete_person_rule", root)

    @staticmethod
    def resolve_can_change_password(root, info, **kwargs):
        return info.context.user.has_perm(
            "core.change_password_rule", root
        ) or info.context.user.has_perm("core.change_user_password_rule", root)

    @staticmethod
    def resolve_can_send_password_reset_request(root, info, **kwargs):
        return info.context.user.has_perm("core.reset_user_password_rule", root)


class AddressInputType(graphene.InputObjectType):
    street = graphene.String(required=False)
    housenumber = graphene.String(required=False)
    postal_code = graphene.String(required=False)
    place = graphene.String(required=False)
    country = graphene.String(required=False)


class PersonInputType(graphene.InputObjectType):
    id = graphene.ID(required=False)  # noqa

    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    additional_name = graphene.String(required=False)
    short_name = graphene.String(required=False)

    street = graphene.String(required=False)
    housenumber = graphene.String(required=False)
    postal_code = graphene.String(required=False)
    place = graphene.String(required=False)

    phone_number = graphene.String(required=False)
    mobile_number = graphene.String(required=False)

    email = graphene.String(required=False)

    date_of_birth = graphene.Date(required=False)
    place_of_birth = graphene.String(required=False)
    sex = graphene.String(required=False)

    address = graphene.Field(AddressInputType, required=False)
    street = graphene.String(required=False)
    housenumber = graphene.String(required=False)
    postal_code = graphene.String(required=False)
    place = graphene.String(required=False)
    country = graphene.String(required=False)

    photo = Upload()
    avatar = Upload()

    guardians = graphene.List(lambda: PersonInputType, required=False)

    # TODO: Primary Group

    description = graphene.String(required=False)


class PersonBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = Person
        permissions = ("core.delete_person_rule",)


class PersonGuardianMutationMixin:
    """Add functionality to handle guardians input to mutations."""

    @classmethod
    def _handle_guardians(cls, root, info, input, obj):  # noqa: A002
        """Handle and save guardian input."""
        guardian_role = Role.objects.get(short_name="guardian")

        if "guardians" in input:
            current_guardian_relationships = PersonRelationship.objects.filter(
                of_person=obj,
                roles=guardian_role,
            )

            handled_guardians = set()

            for relationship in current_guardian_relationships:
                if relationship.person.pk in input["guardians"]:
                    handled_guardians.add(relationship.person.pk)
                else:
                    relationship.delete()

            for new_guardian in list(set(input["guardians"]) - handled_guardians):
                relationship = PersonRelationship.objects.create(
                    person=Person.objects.get(pk=new_guardian),
                    of_person=obj,
                )
                relationship.roles.add(guardian_role)


class PersonAddressMutationMixin:
    """Add functionality to handle address input to mutations."""

    ADDRESS_FIELDS = ["street", "housenumber", "postal_code", "place", "country"]

    @classmethod
    def _handle_address(cls, root, info, input, obj):  # noqa: A002
        """Handle and save address input."""
        address_type = AddressType.get_default()

        if any((key in input) for key in cls.ADDRESS_FIELDS):
            try:
                address = obj.addresses.get(address_types=address_type)
            except Address.DoesNotExist:
                address = obj.addresses.create()
                address.address_types.add(address_type)

            for key in cls.ADDRESS_FIELDS:
                if key not in input:
                    continue
                setattr(address, key, input[key] or "")

            address.full_clean()
            address.save()

            # Delete address if no address fields are set
            if all(not getattr(address, key) for key in cls.ADDRESS_FIELDS):
                address.delete()


class PersonBatchCreateMutation(
    PersonAddressMutationMixin, PersonGuardianMutationMixin, BaseBatchCreateMutation
):
    class Meta:
        model = Person
        permissions = ("core.create_person_rule",)
        only_fields = (
            "user",
            "first_name",
            "last_name",
            "additional_name",
            "short_name",
            "phone_number",
            "mobile_number",
            "email",
            "date_of_birth",
            "place_of_birth",
            "sex",
            "description",
            "photo",
            "avatar",
            "primary_group",
            "related_persons",
            "related_to_persons",
        )
        optional_fields = (
            "additional_name",
            "short_name",
            "phone_number",
            "mobile_number",
            "email",
            "date_of_birth",
            "place_of_birth",
            "sex",
            "description",
            "photo",
            "avatar",
            "primary_group",
            "related_persons",
            "related_to_persons",
        )
        custom_fields = {
            "street": graphene.String(required=False),
            "housenumber": graphene.String(required=False),
            "postal_code": graphene.String(required=False),
            "place": graphene.String(required=False),
            "country": graphene.String(required=False),
            "guardians": graphene.List(graphene.ID, required=False),
        }

    @classmethod
    def handle_sex(cls, value, name, info):
        if value is None:
            return ""
        return value

    @classmethod
    def after_create_obj(cls, root, info, input, obj, full_input):  # noqa: A002
        super().after_create_obj(root, info, input, obj, full_input)
        cls._handle_address(root, info, input, obj)
        cls._handle_guardians(root, info, input, obj)


class PersonBatchPatchMutation(
    PersonAddressMutationMixin, PersonGuardianMutationMixin, BaseBatchPatchMutation
):
    class Meta:
        model = Person
        permissions = ("core.edit_person_rule",)
        only_fields = (
            "id",
            "user",
            "first_name",
            "last_name",
            "additional_name",
            "short_name",
            "phone_number",
            "mobile_number",
            "email",
            "date_of_birth",
            "place_of_birth",
            "sex",
            "description",
            "photo",
            "avatar",
            "primary_group",
            "related_persons",
            "related_to_persons",
        )
        optional_fields = (
            "user",
            "first_name",
            "last_name",
            "additional_name",
            "short_name",
            "phone_number",
            "mobile_number",
            "email",
            "date_of_birth",
            "place_of_birth",
            "sex",
            "description",
            "photo",
            "avatar",
            "primary_group",
            "related_persons",
            "related_to_persons",
        )
        custom_fields = {
            "street": graphene.String(required=False),
            "housenumber": graphene.String(required=False),
            "postal_code": graphene.String(required=False),
            "place": graphene.String(required=False),
            "country": graphene.String(required=False),
            "guardians": graphene.List(graphene.ID, required=False),
        }

    @classmethod
    def handle_sex(cls, value, name, info):
        if value is None:
            return ""
        return value

    @classmethod
    def after_update_obj(cls, root, info, input, obj, full_input):  # noqa: A002
        super().after_update_obj(root, info, input, obj, full_input)
        if info.context.user.has_perm("core.change_person") or info.context.user.has_perm(
            "core.change_person", obj
        ):
            pass
        elif (
            has_person(info.context.user)
            and obj == info.context.user.person
            and get_site_preferences()["account__editable_fields_person"]
        ):
            for input_key in input:
                if (
                    input_key != "id"
                    and input_key not in get_site_preferences()["account__editable_fields_person"]
                ):
                    raise PermissionDenied(
                        "User not allowed to edit the given fields for own person."
                    )
            pass
        cls._handle_address(root, info, input, obj)
        cls._handle_guardians(root, info, input, obj)


class AccountRegistrationInputType(graphene.InputObjectType):
    from .user import UserInputType  # noqa

    person = graphene.Field(PersonInputType, required=True)
    user = graphene.Field(UserInputType, required=True)
    invitation_code = graphene.String(required=False)


class SendAccountRegistrationMutation(PersonAddressMutationMixin, graphene.Mutation):
    class Arguments:
        account_registration = AccountRegistrationInputType(required=True)

    ok = graphene.Boolean()

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, account_registration: AccountRegistrationInputType):
        # Initialize registering person to indicate that registration is in progress
        info.context._registering_person = None

        invitation = None

        if code := account_registration["invitation_code"]:
            formatted_code = "".join(code.lower().split("-"))
            try:
                invitation = PersonInvitation.objects.get(
                    key=formatted_code,
                )
            except PersonInvitation.DoesNotExist as exc:
                raise SuspiciousOperation from exc

        if not get_site_preferences()["auth__signup_enabled"] and not (
            get_site_preferences()["auth__invite_enabled"] and invitation
        ):
            raise PermissionDenied(_("Signup is not enabled."))

        # Create email
        email = None

        if invitation and invitation.email:
            email = invitation.email
        elif account_registration["user"] is not None:
            email = account_registration["user"]["email"]

        # Check username
        for validator in custom_username_validators:
            try:
                validator(account_registration["user"]["username"])
            except ValidationError as exc:
                raise ValidationError(_("This username is not allowed.")) from exc

        # Create user
        try:
            user = get_user_model().objects.create_user(
                username=account_registration["user"]["username"],
                email=email,
                password=account_registration["user"]["password"],
            )
        except IntegrityError as exc:
            raise ValidationError(_("A user with this username or e-mail already exists.")) from exc

        validate_password(account_registration["user"]["password"], user)

        # Create person if no invitation is given or if invitation isn't linked to a person
        if invitation and invitation.person:
            person = invitation.person
            person.email = email
            person.user = user
            person.save()
        else:
            try:
                person, created = Person.objects.get_or_create(
                    user=user,
                    defaults={
                        "email": email,
                        "first_name": account_registration["person"]["first_name"],
                        "last_name": account_registration["person"]["last_name"],
                    },
                )
            except IntegrityError as exc:
                raise ValidationError(
                    _("A person using the e-mail address %s already exists.") % email
                ) from exc

        # Store contact information in database
        person.email = email

        for field in Person._meta.get_fields():
            if (
                field.name in account_registration["person"]
                and account_registration["person"][field.name] is not None
                and account_registration["person"][field.name] != ""
            ):
                setattr(person, field.name, account_registration["person"][field.name])
        person.full_clean()
        person.save()

        # Store address information
        cls._handle_address(root, info, account_registration["person"], person)

        # Accept invitation, if exists
        if invitation:
            accept_invitation(invitation, info.context, info.context.user)
            inviter_role = get_site_preferences()["auth__inviter_role"]

            if inviter_role is not None and invitation.inviter is not None:
                relationship, __ = PersonRelationship.objects.get_or_create(
                    person=invitation.inviter.person,
                    of_person=person,
                )
                relationship.roles.add(inviter_role)

        person.notify_abount_account_registration()

        _act = Activity(
            title=_("You registered an account"),
            description=_(f"You registered an account with the username {user.username}"),
            app="Core",
            user=person,
        )

        # Store person in request to make it accessible for injected registration mutations
        info.context._registering_person = person

        return SendAccountRegistrationMutation(ok=True)
