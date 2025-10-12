import graphene
from graphene import ObjectType


class AppURLType(ObjectType):
    name = graphene.String(required=True)
    url = graphene.String(required=True)


class CopyrightType(ObjectType):
    years = graphene.String(required=True)
    name = graphene.String(required=True)
    email = graphene.String(required=True)


class LicenceFlagsType(ObjectType):
    isFsfLibre = graphene.Boolean(required=True)
    isOsiApproved = graphene.Boolean(required=True)


class SubLicenceType(ObjectType):
    isDeprecatedLicenseId = graphene.Boolean(default_value=False)
    isFsfLibre = graphene.Boolean(default_value=False)
    isOsiApproved = graphene.Boolean(default_value=False)
    licenseId = graphene.String(required=True)
    name = graphene.String(required=True)
    referenceNumber = graphene.Int(default_value=-1)
    url = graphene.String()


class LicenceType(ObjectType):
    verbose_name = graphene.String(required=True)
    flags = graphene.Field(LicenceFlagsType, required=True)
    licences = graphene.List(SubLicenceType)


class AppType(ObjectType):
    copyrights = graphene.List(CopyrightType)
    licence = graphene.Field(LicenceType)
    name = graphene.String(required=True)
    verbose_name = graphene.String(required=True)
    version = graphene.String()
    urls = graphene.List(AppURLType)

    def resolve_verbose_name(root, info, **kwargs):
        return root.get_name()

    def resolve_version(root, info, **kwargs):
        return root.get_version()

    def resolve_licence(root, info, **kwargs):
        return root.get_licence_dict()

    def resolve_urls(root, info, **kwargs):
        return root.get_urls_dict()

    def resolve_copyrights(root, info, **kwargs):
        return root.get_copyright_dicts()
