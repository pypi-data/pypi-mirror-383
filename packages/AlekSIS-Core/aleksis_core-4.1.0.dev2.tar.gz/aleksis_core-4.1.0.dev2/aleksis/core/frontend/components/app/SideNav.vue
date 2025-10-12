<template>
  <v-navigation-drawer v-model="drawer" tag="aside">
    <!-- TODO: v-model:opened="$route.matched" -->
    <v-list nav density="compact" shaped tag="nav" color="primary">
      <v-list-item
        class="focusable"
        ref="listItem"
        :to="{ name: 'dashboard' }"
        exact
        color="transparent"
      >
        <brand-logo :site-preferences="systemProperties.sitePreferences" />
      </v-list-item>
      <v-list-item
        v-if="permissionStore.checkPermission('core.search_rule')"
        class="search"
      >
        <sidenav-search />
      </v-list-item>
      <template v-if="sideNavMenu">
        <template v-for="menuItem in sideNavMenu" :key="menuItem.name">
          <v-list-group
            v-if="menuItem.subMenu.length > 0"
            :value="menuItem.name"
          >
            <template #activator="{ props }">
              <v-list-item
                v-bind="props"
                :prepend-icon="
                  checkActive(menuItem) && menuItem.iconActive
                    ? menuItem.iconActive
                    : menuItem.icon
                "
              >
                <v-list-item-title
                  >{{
                    !menuItem.rawTitleString
                      ? $t(menuItem.titleKey)
                      : menuItem.rawTitleString
                  }}
                </v-list-item-title>
              </v-list-item>
            </template>
            <v-list-item
              v-for="subMenuItem in menuItem.subMenu"
              :exact="subMenuItem.exact"
              :to="{ name: subMenuItem.name }"
              :target="subMenuItem.newTab ? '_blank' : '_self'"
              :key="subMenuItem.name"
            >
              <template #prepend>
                <v-icon
                  v-if="
                    subMenuItem.iconActive && $route.name === subMenuItem.name
                  "
                >
                  {{ subMenuItem.iconActive }}
                </v-icon>
                <v-icon v-else-if="subMenuItem.icon">
                  {{ subMenuItem.icon }}
                </v-icon>
              </template>
              <v-list-item-title
                >{{
                  !subMenuItem.rawTitleString
                    ? $t(subMenuItem.titleKey)
                    : subMenuItem.rawTitleString
                }}
              </v-list-item-title>
            </v-list-item>
          </v-list-group>
          <v-list-item
            v-else
            :exact="menuItem.exact"
            :to="{ name: menuItem.name }"
            :target="menuItem.newTab ? '_blank' : '_self'"
            :value="menuItem.name"
          >
            <template #prepend>
              <v-icon
                v-if="
                  menuItem.iconActive &&
                  $route.matched.some((route) => route.name === menuItem.name)
                "
              >
                {{ menuItem.iconActive }}
              </v-icon>
              <v-icon v-else-if="menuItem.icon">{{ menuItem.icon }}</v-icon>
            </template>
            <v-list-item-title>{{
              !menuItem.rawTitleString
                ? $t(menuItem.titleKey)
                : menuItem.rawTitleString
            }}</v-list-item-title>
          </v-list-item>
        </template>
      </template>
      <template v-else>
        <v-skeleton-loader class="ma-2" type="list-item@5" />
      </template>
    </v-list>

    <template #append>
      <div class="pa-4 d-flex justify-center align-center">
        <v-spacer />
        <language-form
          :available-languages="systemProperties.availableLanguages"
          :default-language="systemProperties.defaultLanguage"
        />
        <v-spacer />
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup>
import BrandLogo from "./BrandLogo.vue";
import LanguageForm from "./LanguageForm.vue";
import SidenavSearch from "./SidenavSearch.vue";

import { usePermissionStore } from "../../stores/permissionStore";
import { useRoute } from "@/vue-router";

import { defineProps, defineModel, nextTick, ref } from "vue";

const drawer = defineModel({ required: true, type: [Boolean, null] });

defineProps({
  sideNavMenu: { type: Array, required: false, default: null },
  systemProperties: { type: Object, required: true },
});

const permissionStore = usePermissionStore();
permissionStore.addPermissions(["core.search_rule"]);

const listItem = ref(null);

const $route = useRoute();

function checkActive(menuItem) {
  if ($route.matched.some((route) => route.name === menuItem.name)) {
    return true;
  }
  if (
    menuItem.subMenu.some((subMenuItem) =>
      this.$route.matched.some((route) => route.name === subMenuItem.name),
    )
  ) {
    return true;
  }
  return false;
}
</script>

<style scoped>
.v-list-group__items .v-list-item {
  padding-inline-start: 24px !important;
}
</style>
