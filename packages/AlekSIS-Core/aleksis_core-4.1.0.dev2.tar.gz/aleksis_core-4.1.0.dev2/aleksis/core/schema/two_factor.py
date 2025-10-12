from dataclasses import dataclass

from django.core.exceptions import PermissionDenied

import graphene
import qrcode
from allauth.account.internal.flows.reauthentication import (
    did_recently_authenticate,
    raise_if_reauthentication_required,
)
from allauth.mfa.adapter import DefaultMFAAdapter, get_adapter
from allauth.mfa.internal.flows.add import validate_can_add_authenticator
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.flows import (
    can_generate_recovery_codes,
    generate_recovery_codes,
)
from allauth.mfa.totp.internal import auth as totp_auth
from allauth.mfa.totp.internal import flows as totp_flows
from allauth.mfa.webauthn.internal import (
    auth as webauthn_auth,
)
from allauth.mfa.webauthn.internal import (
    flows as webauthn_flows,
)
from graphene import ObjectType
from qrcode.image.svg import SvgPathFillImage


class MFATOTPType(ObjectType):
    id = graphene.ID(required=False)
    activated = graphene.Boolean()
    secret = graphene.String(required=False)
    totp_url = graphene.String(required=False)
    totp_qr_code = graphene.String(required=False)

    def resolve_activated(root, info, **kwargs):
        return isinstance(root, Authenticator)

    def resolve_totp_qr_code(root, info, **kwargs):
        if not getattr(root, "totp_url", None):
            return None
        return qrcode.make(root.totp_url, image_factory=SvgPathFillImage).to_string(
            encoding="unicode"
        )


class MFARecoveryCodesType(ObjectType):
    unused_codes = graphene.List(graphene.String)
    unused_code_count = graphene.Int()
    total_code_count = graphene.Int()

    def resolve_total_code_count(root, info, **kwargs):
        return len(root.generate_codes())

    def resolve_unused_code_count(root, info, **kwargs):
        return len(root.get_unused_codes())

    def resolve_unused_codes(root, info, **kwargs):
        raise_if_reauthentication_required(info.context)
        return root.get_unused_codes()


class MFAWebauthnAuthenticatorType(ObjectType):
    id = graphene.ID()
    created_at = graphene.DateTime(required=False)
    last_used_at = graphene.DateTime()
    name = graphene.String()

    @staticmethod
    def resolve_id(root, info, **kwargs):
        return root.instance.id

    @staticmethod
    def resolve_created_at(root, info, **kwargs):
        return root.instance.created_at

    @staticmethod
    def resolve_last_used_at(root, info, **kwargs):
        return root.instance.last_used_at if root.instance.last_used_at else None


class MFAWebauthnType(ObjectType):
    credential_creation_options = graphene.JSONString()
    authenticators = graphene.List(MFAWebauthnAuthenticatorType)

    @staticmethod
    def resolve_credential_creation_options(root, info, **kwargs):
        validate_can_add_authenticator(info.context.user)
        creation_options = webauthn_flows.begin_registration(info.context, info.context.user, False)
        return creation_options

    @staticmethod
    def resolve_authenticators(root, info, **kwargs):
        return [
            a.wrap()
            for a in Authenticator.objects.filter(
                user=info.context.user,
                type=Authenticator.Type.WEBAUTHN,
            )
        ]


class TwoFactorType(ObjectType):
    totp = graphene.Field(MFATOTPType, required=False)
    recovery_codes = graphene.Field(MFARecoveryCodesType, required=False)
    did_recently_authenticate = graphene.Boolean()
    webauthn = graphene.Field(MFAWebauthnType)

    def resolve_did_recently_authenticate(root, info, **kwargs):
        return did_recently_authenticate(info.context)

    def resolve_totp(root, info, **kwargs):
        authenticator = Authenticator.objects.filter(
            type=Authenticator.Type.TOTP, user=info.context.user
        ).first()
        if not authenticator:
            err = validate_can_add_authenticator(info.context.user)
            if err:
                raise ValueError()
            adapter: DefaultMFAAdapter = get_adapter()
            secret = totp_auth.get_totp_secret(regenerate=True)
            totp_url = adapter.build_totp_url(info.context.user, secret)
            return MFATOTPType(secret=secret, totp_url=totp_url)
        return authenticator

    def resolve_recovery_codes(root, info, **kwargs):
        authenticator = Authenticator.objects.filter(
            user=info.context.user,
            type=Authenticator.Type.RECOVERY_CODES,
        ).first()
        if not authenticator:
            return None
        return authenticator.wrap()

    @staticmethod
    def resolve_webauthn(root, info, **kwargs):
        return True


@dataclass
class ActivateTOTPInput:
    secret: str


class ActivateTOTPMutation(graphene.Mutation):
    class Arguments:
        code = graphene.String(required=True)

    authenticator = graphene.Field(MFATOTPType)

    @classmethod
    def mutate(cls, root, info, **data):
        validate_can_add_authenticator(info.context.user)

        secret = totp_auth.get_totp_secret(regenerate=False)
        code = data["code"]
        if not totp_auth.validate_totp_code(secret, code):
            raise get_adapter().validation_error("incorrect_code")

        authenticator = totp_flows.activate_totp(info.context, ActivateTOTPInput(secret=secret))[0]

        return ActivateTOTPMutation(authenticator=authenticator)


class DeactivateAuthenticatorMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **data):
        authenticator = Authenticator.objects.get(id=data["id"], user=info.context.user)

        if authenticator.type == Authenticator.Type.TOTP:
            totp_flows.deactivate_totp(info.context, authenticator)
        elif authenticator.type == Authenticator.Type.WEBAUTHN:
            webauthn_flows.remove_authenticator(info.context, authenticator)
        else:
            raise PermissionDenied()

        return DeactivateAuthenticatorMutation(success=True)


class GenerateRecoveryCodesMutation(graphene.Mutation):
    authenticator = graphene.Field(MFARecoveryCodesType)

    @classmethod
    def mutate(cls, root, info, **data):
        if not can_generate_recovery_codes(info.context.user):
            raise get_adapter().validation_error("cannot_generate_recovery_codes")
        authenticator = generate_recovery_codes(info.context)

        return GenerateRecoveryCodesMutation(authenticator=authenticator.wrap())


class AddSecurityKeyMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        credential = graphene.JSONString(required=True)

    authenticator = graphene.Field(MFAWebauthnAuthenticatorType)

    @classmethod
    def mutate(cls, root, info, **data):
        validate_can_add_authenticator(info.context.user)

        credential = data["credential"]
        webauthn_auth.parse_registration_response(credential)
        webauthn_auth.complete_registration(credential)

        authenticator = webauthn_flows.add_authenticator(
            info.context,
            name=data["name"],
            credential=data["credential"],
        )[0]

        return AddSecurityKeyMutation(authenticator=authenticator.wrap())
