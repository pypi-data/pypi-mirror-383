from aleksis.core.models import CalendarWidget, ExternalLinkWidget, StaticContentWidget
from aleksis.core.schema.base import BaseBatchPatchMutation, BaseObjectType
from aleksis.core.schema.dashboard.dashboard import DashboardWidgetType


class ExternalLinkWidgetType(BaseObjectType):
    class Meta:
        model = ExternalLinkWidget
        interfaces = (DashboardWidgetType,)
        fields = ["url", "icon_url"]


class StaticContentWidgetType(BaseObjectType):
    class Meta:
        model = StaticContentWidget
        interfaces = (DashboardWidgetType,)
        fields = ["content"]


class CalendarWidgetType(BaseObjectType):
    class Meta:
        model = CalendarWidget
        interfaces = (DashboardWidgetType,)
        fields = ["selected_calendars"]


class CalendarWidgetBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = CalendarWidget
        permissions = ("core.edit_dashboardwidget_rule",)
        fields = (
            "id",
            "status",
            "title",
            "selected_calendars",
        )
        return_field_name = "dashboardWidgets"


class StaticContentWidgetBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = StaticContentWidget
        permissions = ("core.edit_dashboardwidget_rule",)
        fields = (
            "id",
            "status",
            "title",
            "content",
        )
        return_field_name = "dashboardWidgets"


class ExternalLinkWidgetBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = ExternalLinkWidget
        permissions = ("core.edit_dashboardwidget_rule",)
        fields = (
            "id",
            "status",
            "title",
            "url",
            "icon_url",
        )
        return_field_name = "dashboardWidgets"


dashboard_types = [
    ExternalLinkWidgetType,
    StaticContentWidgetType,
    CalendarWidgetType,
]
