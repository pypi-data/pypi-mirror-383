import { useRouter } from "@/vue-router";
import { ref } from "vue";
import { usePermissionStore } from "../../stores/permissionStore";
import { useAppStore } from "../../stores/appStore";

/**
 * Vue composable containing menu generation code.
 *
 * Only used by main App component, but factored out for readability.
 */
export const useMenus = function () {
  const router = useRouter();
  const permissionStore = usePermissionStore();
  const appStore = useAppStore();

  /**
   * Get all permission names used in the routes.
   */
  function getPermissionNames() {
    let permArray = [];

    for (const route of router.getRoutes()) {
      if (route.meta) {
        if (
          route.meta["permission"] &&
          !(route.meta["permission"] in permArray)
        ) {
          permArray.push(route.meta["permission"]);
        }
        if (
          route.meta["menuPermission"] &&
          !(route.meta["menuPermission"] in permArray)
        ) {
          permArray.push(route.meta["menuPermission"]);
        }
      }
    }

    permissionStore.addPermissions(permArray);
  }

  function checkValidators(validators) {
    for (const validator of validators) {
      if (
        !validator(
          appStore.whoAmI,
          null,
          // TODO:
          // systemProperties,
        )
      ) {
        return false;
      }
    }
    return true;
  }

  /**
   * Build a menu from the given routes.
   *
   * @param {Array} routes Routes to build the menu from.
   * @param {string} menuKey Key to use for the menu entries.
   * @returns {Object} The built menu.
   */
  function buildMenu(routes, menuKey) {
    let menu = {};
    let childrenRoutes = {};

    // Top-level entries
    for (const route of routes) {
      if (
        route.name &&
        route.meta &&
        route.meta[menuKey] &&
        (route.meta?.parent || route.children.length > 0) &&
        (route.meta.menuPermission
          ? permissionStore.checkPermission(route.meta.menuPermission)
          : route.meta.permission
            ? permissionStore.checkPermission(route.meta.permission)
            : true) &&
        (route.meta.validators
          ? checkValidators(route.meta.validators)
          : true) &&
        !route.meta.hide
      ) {
        console.log(route.name);
        let menuItem = {
          ...route.meta,
          name: route.name,
          path: route.path,
          subMenu: [],
        };
        if (!menuItem.order) {
          menuItem.order = 1000000;
        }
        menu[menuItem.name] = menuItem;
      }

      if (route.children.length > 0) {
        for (const childRoute of route.children) {
          childrenRoutes[childRoute.name] = route.name;
        }
      }
    }

    // Sub menu entries
    for (const route of routes) {
      if (!(route.name in childrenRoutes)) continue;
      let parentName = childrenRoutes[route.name];
      // Put object routes into their normal app menu
      if (parentName.startsWith("objects.")) {
        parentName = parentName.slice("objects.".length);
      }
      if (
        route.name &&
        route.meta &&
        route.meta[menuKey] &&
        parentName in menu &&
        (route.meta.menuPermission
          ? permissionStore.checkPermission(route.meta.menuPermission)
          : route.meta.permission
            ? permissionStore.checkPermission(route.meta.permission)
            : true) &&
        (route.meta.validators
          ? checkValidators(route.meta.validators)
          : true) &&
        !route.meta.hide
      ) {
        let menuItem = {
          ...route.meta,
          name: route.name,
          path: route.path,
          subMenu: [],
        };
        if (!menuItem.order) {
          menuItem.order = 1000000;
        }
        menu[parentName].subMenu.push(menuItem);
      }
    }

    for (const [key, value] of Object.entries(menu)) {
      menu[key].subMenu.sort((a, b) => a.order - b.order);
    }

    return Object.values(menu).toSorted((a, b) => a.order - b.order);
  }

  const accountMenu = ref([]);
  const sideNavMenu = ref([]);

  function initMenus() {
    getPermissionNames();

    accountMenu.value = buildMenu(router.getRoutes(), "inAccountMenu");
    sideNavMenu.value = buildMenu(router.getRoutes(), "inMenu");
  }

  return {
    sideNavMenu,
    accountMenu,
    initMenus,
  };
};
