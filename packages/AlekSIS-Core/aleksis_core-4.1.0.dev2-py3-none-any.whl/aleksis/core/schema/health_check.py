import graphene


class HealthCheckPluginType(graphene.ObjectType):
    status = graphene.String()
    pretty_status = graphene.String()
    identifier = graphene.String()
    time_taken = graphene.Int()

    def resolve_pretty_status(root, info, **kwargs):
        return root.pretty_status()

    def resolve_identifier(root, info, **kwargs):
        return root.identifier()
