import { collections } from "aleksisAppImporter";
import gql from "graphql-tag";

export function buildQuery() {
  const widgets = collections.coreDashboardWidgets.items;

  let fragments = widgets.filter((w) => !!w.fragment).map((w) => w.fragment);
  let fragmentNames = widgets
    .filter((w) => !!w.fragment)
    .map((w) => "..." + w.typename + "Fragment")
    .join("\n");

  return gql(
    [
      `
      query dashboardWidgets($status: Status) {
        dashboard {
          widgets(status: $status) {
            __typename
            id
            status
            title

            canEdit
            canDelete

            ${fragmentNames}
          }
        }
      }
      `,
      ...fragments.map(() => ""),
    ],
    ...fragments,
  );
}

export function buildCreateMutation() {
  const widgets = collections.coreDashboardWidgets.items;

  let fragments = widgets.filter((w) => !!w.fragment).map((w) => w.fragment);
  let fragmentNames = widgets
    .filter((w) => !!w.fragment)
    .map((w) => "..." + w.typename + "Fragment")
    .join("\n");

  return gql(
    [
      `
      mutation createDashboardWidgets($widgetTypes: [String]!) {
        createDashboardWidgets(widgetTypes: $widgetTypes) {
          items: created {
            __typename
            id
            status
            title

            canDelete
            canEdit

            ${fragmentNames}
          }
        }
      }
      `,
      ...fragments.map(() => ""),
    ],
    ...fragments,
  );
}
