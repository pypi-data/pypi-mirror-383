import graphene


class SearchModelType(graphene.ObjectType):
    absolute_url = graphene.String()
    name = graphene.String()
    icon = graphene.String()

    def resolve_absolute_url(root, info, **kwargs):
        if hasattr(root, "get_absolute_url"):
            return root.get_absolute_url()
        else:
            return "#!"

    def resolve_name(root, info, **kwargs):
        return str(root)

    def resolve_icon(root, info, **kwargs):
        return getattr(root, "icon_", "")


class SearchResultType(graphene.ObjectType):
    app_label = graphene.String()
    model_name = graphene.String()
    score = graphene.Int()
    obj = graphene.Field(SearchModelType)
    verbose_name = graphene.String()
    verbose_name_plural = graphene.String()
    text = graphene.String()

    def resolve_obj(root, info, **kwargs):  # noqa
        return root.object
