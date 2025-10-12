import graphene


class GlobalPermissionType(graphene.ObjectType):
    name = graphene.ID()
    result = graphene.Boolean()


class ObjectPermissionInputType(graphene.InputObjectType):
    name = graphene.String()
    obj_id = graphene.String()
    obj_type = graphene.String()
    app_label = graphene.String()


class ObjectPermissionResultType(graphene.ObjectType):
    name = graphene.String()
    obj_id = graphene.String()
    obj_type = graphene.String()
    app_label = graphene.String()
    result = graphene.Boolean()
