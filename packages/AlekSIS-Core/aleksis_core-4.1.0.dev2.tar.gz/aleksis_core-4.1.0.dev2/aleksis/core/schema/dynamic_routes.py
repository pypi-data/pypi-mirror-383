import graphene


class DynamicRouteType(graphene.ObjectType):
    parent_route_name = graphene.String()

    route_path = graphene.String()
    route_name = graphene.String()

    display_account_menu = graphene.Boolean()
    display_sidenav_menu = graphene.Boolean()
    menu_new_tab = graphene.Boolean()

    menu_title = graphene.String()
    menu_icon = graphene.String()

    menu_permission = graphene.String()
    route_permission = graphene.String()
