from django.core.exceptions import PermissionDenied

import graphene
from maintenance_mode.core import set_maintenance_mode


class SetMaintenanceModeMutation(graphene.Mutation):
    class Arguments:
        mode = graphene.Boolean()

    mode = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, mode):
        if not info.context.user.has_perm("core.set_maintenance_mode_rule"):
            raise PermissionDenied()

        set_maintenance_mode(mode)

        return SetMaintenanceModeMutation(mode=mode)
