import gqlDynamicRoutes from "../../components/app/dynamicRoutes.graphql";
import { useQuery } from "../app/apollo";
import { useRouter } from "@/vue-router";

/**
 * Vue composable containing code getting dynamically added routes from other apps.
 *
 * Only used by main App component, but factored out for readability.
 * @param {Function} onUpdate Hook called once routes have been updated
 */
export function useDynamicRoutes(onUpdate) {
  const router = useRouter();

  const { onResult } = useQuery(gqlDynamicRoutes, null, {
    pollInterval: 30000,
  });

  onResult((result) => {
    const dynamicRoutes = result.data.dynamicRoutes || [];

    for (const route of dynamicRoutes) {
      if (route) {
        console.debug("Adding new dynamic route:", route.routeName);
        let routeEntry = {
          path: route.routePath,
          name: route.routeName,
          component: () => import("../../components/LegacyBaseTemplate.vue"),
          props: {
            byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
          },
          meta: {
            inMenu: route.displaySidenavMenu,
            inAccountMenu: route.displayAccountMenu,
            icon: route.menuIcon,
            rawTitleString: route.menuTitle,
            menuPermission: route.menuPermission,
            permission: route.routePermission,
            newTab: route.menuNewTab,
            dynamic: true,
            hide: false,
          },
        };

        if (route.parentRouteName) {
          router.addRoute(route.parentRouteName, routeEntry);
        } else {
          router.addRoute(routeEntry);
        }
      }
    }

    for (const route of router
      .getRoutes()
      .filter((r) => r.meta.dynamic && !r.meta.hide)) {
      if (!(dynamicRoutes.map((r) => r.routeName).indexOf(route.name) > -1)) {
        let hiddenRoute = { ...route, meta: { ...route.meta, hide: true } };
        this.$router.addRoute(hiddenRoute);
      }
    }

    onUpdate();
  });
}
