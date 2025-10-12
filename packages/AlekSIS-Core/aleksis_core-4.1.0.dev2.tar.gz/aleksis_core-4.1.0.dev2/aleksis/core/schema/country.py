import graphene


class CountryType(graphene.ObjectType):
    code = graphene.String()
    name = graphene.String()

    def resolve_code(root, info, **kwargs):
        return root.code

    def resolve_name(root, info, **kwargs):
        return root.name
