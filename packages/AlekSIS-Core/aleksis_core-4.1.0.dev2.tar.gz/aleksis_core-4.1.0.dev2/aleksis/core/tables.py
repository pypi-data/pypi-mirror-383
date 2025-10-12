from textwrap import wrap

from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import A

from .util.core_helpers import get_site_preferences


class InvitationCodeColumn(tables.Column):
    """Returns invitation code in a more readable format."""

    def render(self, value):
        packet_size = get_site_preferences()["auth__invite_code_packet_size"]
        return "-".join(wrap(value, packet_size))


class InvitationsTable(tables.Table):
    """Table to list persons."""

    person = tables.Column()
    email = tables.EmailColumn()
    sent = tables.DateColumn()
    inviter = tables.Column()
    key = InvitationCodeColumn()
    accepted = tables.BooleanColumn(
        yesno="check,cancel", attrs={"span": {"class": "material-icons"}}
    )


class PermissionDeleteColumn(tables.LinkColumn):
    """Link column with label 'Delete'."""

    def __init__(self, url, **kwargs):
        super().__init__(
            url,
            args=[A("pk")],
            text=_("Delete"),
            attrs={"a": {"class": "btn-flat waves-effect waves-red red-text"}},
            verbose_name=_("Actions"),
            **kwargs,
        )


class PermissionTable(tables.Table):
    """Table to list permissions."""

    class Meta:
        attrs = {"class": "responsive-table highlight"}

    permission = tables.Column()


class ObjectPermissionTable(PermissionTable):
    """Table to list object permissions."""

    content_object = tables.Column()


class GlobalPermissionTable(PermissionTable):
    """Table to list global permissions."""

    pass


class GroupObjectPermissionTable(ObjectPermissionTable):
    """Table to list assigned group object permissions."""

    group = tables.Column()
    delete = PermissionDeleteColumn("delete_group_object_permission")


class UserObjectPermissionTable(ObjectPermissionTable):
    """Table to list assigned user object permissions."""

    user = tables.Column()
    delete = PermissionDeleteColumn("delete_user_object_permission")


class GroupGlobalPermissionTable(GlobalPermissionTable):
    """Table to list assigned global user permissions."""

    group = tables.Column()
    delete = PermissionDeleteColumn("delete_group_global_permission")


class UserGlobalPermissionTable(GlobalPermissionTable):
    """Table to list assigned global group permissions."""

    user = tables.Column()
    delete = PermissionDeleteColumn("delete_user_global_permission")
