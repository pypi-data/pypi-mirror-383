import gql from "graphql-tag";
import { defineAsyncComponent } from "vue";

export const collections = [
  {
    name: "groupOverview",
    type: Object,
    items: [
      {
        tab: {
          id: "default",
          titleKey: "group.tabs.members_tab",
        },
        titleKey: "group.tabs.members",
        component: defineAsyncComponent(
          () => import("./components/group/GroupMembers.vue"),
        ),
      },
    ],
  },
  {
    name: "groupActions",
    type: Object,
  },
  {
    name: "personWidgets",
    type: Object,
  },
  {
    name: "accountRegistrationSteps",
    type: Object,
  },
  {
    name: "accountRegistrationExtraMutations",
    type: Object,
  },
  {
    name: "dashboardWidgets",
    type: Object,
  },
];

export const collectionItems = {
  coreGroupActions: [
    {
      key: "core-delete-group-action",
      component: defineAsyncComponent(
        () => import("./components/group/actions/DeleteGroup.vue"),
      ),
      isActive: (group) => group.canDelete || false,
    },
  ],
  coreDashboardWidgets: [
    {
      key: "core-static-content-widget",
      typename: "StaticContentWidgetType",
      fragment: gql`
        fragment StaticContentWidgetTypeFragment on StaticContentWidgetType {
          content
        }
      `,
      nameKey: "dashboard.dashboard_widgets.static_content.name",
      shortNameKey: "dashboard.dashboard_widgets.static_content.shortName",
      component: defineAsyncComponent(
        () =>
          import(
            "./components/dashboard_widget/widgets/static_content/StaticContentWidget.vue"
          ),
      ),
      preview: defineAsyncComponent(
        () =>
          import(
            "./components/dashboard_widget/widgets/static_content/Preview.vue"
          ),
      ),
      management: defineAsyncComponent(
        () =>
          import(
            "./components/dashboard_widget/widgets/static_content/Management.vue"
          ),
      ),
    },
    {
      key: "core-external-link-widget",
      typename: "ExternalLinkWidgetType",
      fragment: gql`
        fragment ExternalLinkWidgetTypeFragment on ExternalLinkWidgetType {
          url
          iconUrl
        }
      `,
      nameKey: "dashboard.dashboard_widgets.external_link.name",
      shortNameKey: "dashboard.dashboard_widgets.external_link.shortName",
      component: defineAsyncComponent(
        () =>
          import(
            "./components/dashboard_widget/widgets/external_link/ExternalLinkWidget.vue"
          ),
      ),
      preview: defineAsyncComponent(
        () =>
          import(
            "./components/dashboard_widget/widgets/external_link/Preview.vue"
          ),
      ),
      management: defineAsyncComponent(
        () =>
          import(
            "./components/dashboard_widget/widgets/external_link/Management.vue"
          ),
      ),
    },
    {
      key: "core-calendar-widget",
      typename: "CalendarWidgetType",
      fragment: gql`
        fragment CalendarWidgetTypeFragment on CalendarWidgetType {
          selectedCalendars
        }
      `,
      nameKey: "dashboard.dashboard_widgets.calendar.name",
      shortNameKey: "dashboard.dashboard_widgets.calendar.shortName",
      component: defineAsyncComponent(
        () =>
          import(
            "./components/dashboard_widget/widgets/calendar/CalendarWidget.vue"
          ),
      ),
      preview: defineAsyncComponent(
        () =>
          import("./components/dashboard_widget/widgets/calendar/Preview.vue"),
      ),
      management: defineAsyncComponent(
        () =>
          import(
            "./components/dashboard_widget/widgets/calendar/Management.vue"
          ),
      ),
    },
  ],
};
