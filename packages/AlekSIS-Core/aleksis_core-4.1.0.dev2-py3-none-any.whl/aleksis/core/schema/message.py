import graphene


class MessageType(graphene.ObjectType):
    tags = graphene.String()
    message = graphene.String()

    def resolve_tags(root, info, **kwargs):
        return root.tags

    def resolve_message(root, info, **kwargs):
        return root.message
