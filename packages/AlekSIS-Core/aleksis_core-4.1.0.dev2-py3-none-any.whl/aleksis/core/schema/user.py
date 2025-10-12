from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import BadRequest, PermissionDenied, ValidationError
from django.utils.translation import gettext as _

import graphene
from allauth.account.internal import flows
from allauth.account.internal.flows.password_reset import request_password_reset
from allauth.headless.account.inputs import ResetPasswordKeyInput

from .permissions import GlobalPermissionType
from .person import PersonType


class UserType(graphene.ObjectType):
    id = graphene.ID()  # noqa
    username = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()

    is_authenticated = graphene.Boolean(required=True)
    is_anonymous = graphene.Boolean(required=True)
    is_impersonate = graphene.Boolean()

    person = graphene.Field(PersonType)

    global_permissions_by_name = graphene.List(
        GlobalPermissionType, permissions=graphene.List(graphene.String)
    )

    def resolve_global_permissions_by_name(root, info, permissions, **kwargs):
        return [
            {"name": permission_name, "result": info.context.user.has_perm(permission_name)}
            for permission_name in permissions
        ]


class UserInputType(graphene.InputObjectType):
    username = graphene.String(required=True)
    first_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    email = graphene.String(required=False)
    password = graphene.String(required=True)


class RequestPasswordResetMutation(graphene.Mutation):
    """Mutation for requesting a password reset email."""

    class Arguments:
        user_id = graphene.ID(required=False)
        email = graphene.String(required=False)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, user_id=None, email=None):
        if user_id and email:
            raise BadRequest()
        try:
            if user_id:
                user = get_user_model().objects.get(pk=user_id)
            else:
                user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return RequestPasswordResetMutation(success=True)

        if user_id and not info.context.user.has_perm("core.reset_user_password_rule", user):
            raise PermissionDenied()
        if email and not info.context.user.has_perm("core.reset_password_rule"):
            raise PermissionDenied()

        request_password_reset(info.context, email, [user], None)
        return RequestPasswordResetMutation(success=True)


def check_password_reset_key(root, info, key) -> bool:
    """Check if a password reset key is valid."""
    data = ResetPasswordKeyInput({"key": key})
    return data.is_valid()


class ChangePasswordMutation(graphene.Mutation):
    """Change the password of a user."""

    class Arguments:
        user_id = graphene.ID(required=False)
        old_password = graphene.String(required=False)
        reset_key = graphene.String(required=False)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, password, user_id=None, old_password=None, reset_key=None):
        # Three valid combinations of inputs:
        # ID + PW → change password from somebody else
        # OLD_PW + PW → change password from user in request
        # KEY + PW → set password after reset for user affiliated with key

        if sum(map(bool, [user_id, old_password, reset_key])) != 1:
            raise BadRequest()

        if reset_key is not None:
            data = ResetPasswordKeyInput({"key": reset_key})
            if not data.is_valid():
                raise ValidationError("The reset key is not valid.")
            user = data.user
        elif user_id is not None:
            user = get_user_model().objects.get(pk=user_id)
            if (
                not user
                or not user.person
                or not info.context.user.has_perm("core.change_user_password_rule", user.person)
            ):
                raise PermissionDenied()
        elif old_password is not None:
            if not info.context.user.has_perm("core.change_password_rule"):
                raise ValidationError(_("Changing passwords is not allowed."))
            if not info.context.user.check_password(old_password):
                raise ValidationError(_("Please enter the correct old password."))
            user = info.context.user
        else:
            # Should be handled by the check beforehand
            raise BadRequest()

        # Validate new password
        validate_password(password, user)

        flows.password_change.change_password(user, password)

        if old_password is not None:
            flows.password_change.finalize_password_change(info.context, user)
        else:
            flows.password_change.finalize_password_set(info.context, user)

        return ChangePasswordMutation(success=True, user=user)
