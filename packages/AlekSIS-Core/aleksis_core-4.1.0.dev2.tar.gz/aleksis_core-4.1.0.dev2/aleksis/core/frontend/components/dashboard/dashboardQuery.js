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
        query dashboardWidgets($forceDefault: Boolean) {
          dashboard {
            hasOwn
            my(forceDefault: $forceDefault) {
              id
              x
              y
              width
              height
              context
              widget {
                __typename
                id
                status
                title

                ${fragmentNames}
              }
            }
          }
        }
      `,
      ...fragments.map(() => ""),
    ],
    ...fragments,
  );
}
