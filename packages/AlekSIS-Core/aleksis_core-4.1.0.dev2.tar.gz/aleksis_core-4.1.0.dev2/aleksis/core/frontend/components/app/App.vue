<!--
  Main App component.

  This component contains the outer app UI of AlekSIS and all behaviour
  that is always on-screen, independent of the specific page.
-->

<script setup>
import ActiveSchoolTermSelect from "../school_term/ActiveSchoolTermSelect.vue";
import ActiveSchoolTermBanner from "../school_term/ActiveSchoolTermBanner.vue";
import AccountMenu from "./AccountMenu.vue";
import AnnouncementBanner from "../announcements/AnnouncementBanner.vue";
import NotificationList from "../notifications/NotificationList.vue";
import CeleryProgressBottom from "../celery_progress/CeleryProgressBottom.vue";
import Splash from "./Splash.vue";
import SideNav from "./SideNav.vue";
import ErrorPage from "./ErrorPage.vue";
import Mascot from "../generic/mascot/Mascot.vue";

import gqlAnnouncements from "./announcements.graphql";
import gqlMessages from "./messages.graphql";
import gqlWhoAmI from "./whoAmI.graphql";
import gqlObjectPermissions from "./objectPermissions.graphql";
import { gqlSystemProperties } from "./systemProperties.graphql";

import { useQuery } from "../../composables/app/apollo";
import { useServiceWorker } from "../../composables/setup/serviceWorker";
import { useOffline } from "../../composables/setup/offline";
import { useFooterMenu } from "../../composables/setup/footerMenu";
import { useMenus } from "../../composables/setup/menus";
import { useDynamicRoutes } from "../../composables/setup/dynamicRoutes";
import { useError404 } from "../../composables/setup/error404";
import { useTheming } from "../../composables/setup/theming";
import { useLegacyBaseTemplate } from "../../composables/app/legacyBaseTemplate";

import { browsersRegex } from "virtual:supported-browsers";

import { useAppStore } from "../../stores/appStore";
import { usePermissionStore } from "../../stores/permissionStore";

import { onMounted, reactive, ref, computed, watch } from "vue";
import { useRoute, useRouter } from "@/vue-router";
import { useTheme } from "vuetify";

const { isError404, initRouterFor404 } = useError404();
const error404 = reactive(isError404);

const { initMenus, accountMenu: accountMenuData, sideNavMenu } = useMenus();
const { updateServiceWorker, needRefresh } = useServiceWorker();

const appStore = useAppStore();
const permissionStore = usePermissionStore();

onMounted(() => {
  // Initialize the router for error404 handling
  initRouterFor404();
  useRouter().isReady().then(initMenus);
});

const { result, onResult: onWhoAmI } = useQuery(
  gqlWhoAmI,
  computed(() => ({ permissions: permissionStore.permissionNames })),
  {
    pollInterval: 30000,
  },
);

onWhoAmI(({ data }) => {
  if (data && data.whoAmI) {
    appStore.whoAmI = data.whoAmI;
    permissionStore.setPermissionResults(data.whoAmI.permissions);
  }
  initMenus();
});

const whoAmI = computed(() => result.value?.whoAmI || null);

const { onResult: onObjectPermissions } = useQuery(
  gqlObjectPermissions,
  () => ({
    input: permissionStore.objectPermissionItems,
  }),
);

onObjectPermissions(({ data }) => {
  if (data) {
    permissionStore.setObjectPermissionResults(data.objectPermissions);
  }
});

const systemProperties = ref(null);

const { loading: systemPropertiesLoading, onResult: onSystemProperties } =
  useQuery(gqlSystemProperties);

const theme = useTheme();

onSystemProperties(({ data }) => {
  systemProperties.value = data.systemProperties;

  const primary = data.systemProperties.sitePreferences.themePrimary;
  const secondary = data.systemProperties.sitePreferences.themeSecondary;
  const design = data.systemProperties.sitePreferences.themeDesign;

  useTheming(theme, primary, secondary, design);
});

useOffline();

useDynamicRoutes(initMenus);

const { footerMenu } = useFooterMenu();

const browserCompatible = computed(() =>
  browsersRegex.test(navigator.userAgent),
);

const { isLegacyBaseTemplate } = useLegacyBaseTemplate();

function routeComponentMounted() {
  if (!isLegacyBaseTemplate.value) {
    appStore.setContentLoading(false);
  }
}

const drawer = ref(null);

watch(drawer, (newValue) => {
  if (newValue) {
    // Drawer was opened, → focus sidenav
    // TODO
    // this.$refs.sidenav.focusList();
  }
});

const {
  loading: messagesLoading,
  result: messagesResult,
  refetch: refetchMessages,
} = useQuery(gqlMessages);

const route = useRoute();

const messages = computed(() =>
  messagesLoading.value ? [] : messagesResult.value.messages,
);

const { loading: announcementsLoading, result: announcementsResult } =
  useQuery(gqlAnnouncements);

const announcements = computed(() =>
  announcementsLoading.value ? [] : announcementsResult.value.announcements,
);

watch(
  () => route.fullPath,
  () => {
    console.log("Route Path changed, fetching messages");
    refetchMessages();
  },
  { immediate: true },
);
</script>

<template>
  <v-app v-cloak>
    <splash v-if="systemPropertiesLoading && !systemProperties" splash />
    <error-page
      v-else-if="!browserCompatible"
      short-error-message-key="browser_errors.incompatible_browser"
      long-error-message-key="browser_errors.browsers_compatibility"
      hide-button="true"
      mascot-type="broken"
    />
    <div v-else-if="systemProperties">
      <side-nav
        ref="sidenav"
        v-model="drawer"
        :system-properties="systemProperties"
        :side-nav-menu="sideNavMenu"
      ></side-nav>
      <v-app-bar color="primary">
        <v-app-bar-nav-icon
          @click="drawer = !drawer"
          color="on-primary"
          :aria-label="$t('actions.toggle_sidenav')"
        />

        <v-toolbar-title>
          <router-link
            class="text-on-primary text-decoration-none"
            :to="{ name: 'dashboard' }"
          >
            {{ appStore.toolbarTitle }}
          </router-link>
        </v-toolbar-title>

        <v-progress-linear
          :active="appStore.contentLoading"
          :indeterminate="appStore.contentLoading"
          absolute
          location="bottom"
          :color="$vuetify.theme.name === 'dark' ? 'primary' : 'grey lighten-3'"
          aria-hidden="true"
        />

        <v-spacer />
        <div
          v-if="whoAmI && whoAmI.isAuthenticated && whoAmI.person"
          class="d-flex align-center px-2"
        >
          <active-school-term-select v-model="$root.activeSchoolTerm" />
          <notification-list v-if="!whoAmI.person.isDummy" />
          <account-menu
            :account-menu="accountMenuData"
            :system-properties="systemProperties"
            :who-am-i="whoAmI"
          ></account-menu>
        </div>
      </v-app-bar>
      <v-main>
        <active-school-term-banner
          v-if="$root.activeSchoolTerm && !$root.activeSchoolTerm.current"
        />

        <announcement-banner
          v-for="announcement in announcements"
          :key="announcement.id"
          :announcement="announcement"
        />

        <div
          :class="{
            'main-container': true,
            'pa-3': true,
            'full-width': $route.meta.fullWidth,
          }"
        >
          <message-box type="warning" v-if="appStore.maintenance" class="pa-1">
            <template #prepend>
              <mascot type="broken" max-width="64px" max-height="64px" />
            </template>
            {{ $t("network_errors.service_unavailable") }}
          </message-box>

          <message-box type="warning" v-else-if="appStore.offline" class="pa-1">
            <template #prepend>
              <mascot type="offline" max-width="64px" max-height="64px" />
            </template>
            {{ $t("network_errors.offline_notification") }}
          </message-box>

          <message-box
            type="error"
            v-if="whoAmI && whoAmI.person && whoAmI.person.isDummy"
          >
            {{ $t("base.person_is_dummy") }}
          </message-box>
          <message-box
            type="error"
            v-else-if="whoAmI && !whoAmI.person && !whoAmI.isAnonymous"
          >
            {{ $t("base.user_not_linked_to_person") }}
          </message-box>

          <div v-if="messages">
            <message-box
              v-for="(message, idx) in messages"
              :type="message.tags"
              :key="idx"
              >{{ message.message }}
            </message-box>
          </div>

          <error-page
            v-if="error404"
            short-error-message-key="network_errors.error_404"
            long-error-message-key="network_errors.page_not_found"
            redirect-button-text-key="network_errors.back_to_start"
            redirect-route-name="dashboard"
            redirect-button-icon="$home"
            mascot-type="not_found"
          >
          </error-page>
          <router-view
            v-else-if="
              !$route.meta.permission ||
              permissionStore.checkPermission($route.meta.permission) ||
              $route.name === 'dashboard'
            "
            @mounted="routeComponentMounted"
          />
          <error-page
            v-else-if="
              whoAmI &&
              !$apollo.queries.whoAmI.loading &&
              !checkPermission($route.meta.permission)
            "
            short-error-message-key="base.no_permission_message_short"
            :long-error-message-key="
              whoAmI?.userid
                ? 'base.no_permission_message_long'
                : 'base.no_permission_message_long_not_logged_in'
            "
            redirect-button-text-key="base.no_permission_redirect_text"
            redirect-route-name="core.accounts.login"
            :redirect-route-args="{ query: { next: $route.fullPath } }"
            redirect-button-icon="mdi-login-variant"
            mascot-type="forbidden"
          >
          </error-page>
        </div>
      </v-main>

      <celery-progress-bottom v-if="whoAmI && !whoAmI.isAnonymous" />

      <v-footer app absolute class="pa-0 d-flex" color="primary-lighten-1">
        <v-card flat tile class="bg-primary text-on-primary flex-grow-1">
          <div v-if="footerMenu && footerMenu.items">
            <v-card-text class="pa-0">
              <v-container class="px-6">
                <v-row justify="center" no-gutters>
                  <v-btn
                    v-for="menu_item in footerMenu.items"
                    :key="menu_item.name"
                    variant="text"
                    rounded
                    :href="menu_item.url"
                    color="on-primary"
                    class="ma-2"
                  >
                    <v-icon v-if="menu_item.icon" start>{{
                      "mdi-" + menu_item.icon
                    }}</v-icon>
                    {{ menu_item.name }}
                  </v-btn>
                </v-row>
              </v-container>
            </v-card-text>
            <v-divider />
          </div>

          <v-card-text class="pa-0">
            <v-container class="px-6">
              <v-row>
                <v-col
                  class="text-on-primary d-flex align-center text-subtitle-2"
                >
                  <div>
                    <router-link
                      :to="{ name: 'core.about' }"
                      class="text-on-primary text-decoration-none"
                      >{{ $t("base.about_aleksis") }}
                    </router-link>
                    <span>{{ $t("base.about_copyright") }}</span>
                  </div>
                </v-col>
                <v-col class="d-flex justify-end">
                  <v-btn
                    v-if="systemProperties.sitePreferences.footerImprintUrl"
                    size="small"
                    variant="text"
                    :href="systemProperties.sitePreferences.footerImprintUrl"
                    color="on-primary"
                  >
                    {{ $t("base.imprint") }}
                  </v-btn>
                  <v-btn
                    v-if="systemProperties.sitePreferences.footerPrivacyUrl"
                    size="small"
                    variant="text"
                    :href="systemProperties.sitePreferences.footerPrivacyUrl"
                    color="on-primary"
                  >
                    {{ $t("base.privacy_policy") }}
                  </v-btn>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
        </v-card>
      </v-footer>
    </div>
    <v-snackbar-queue v-model="appStore.snackbarItems" location="top right" />
    <v-dialog :model-value="needRefresh" persistent max-width="400px">
      <v-card>
        <v-card-title>
          {{ $t("service_worker.new_version_available.header") }}
        </v-card-title>

        <v-card-text>
          {{
            $t("service_worker.new_version_available.body", {
              instance: appStore.pageBaseTitle,
            })
          }}
        </v-card-text>

        <v-card-actions>
          <v-spacer />

          <v-btn color="primary" variant="text" @click="updateServiceWorker()">
            <v-icon start>$updatePwa</v-icon>
            {{ $t("service_worker.update") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<style>
div[aria-required="true"] .v-input .v-label::after {
  content: " *";
  color: var(--v-theme-error);
}

.main-container {
  margin-inline: auto;
  max-width: 1440px;
  width: 96%;
  margin-bottom: 1rem;
}
.main-container.full-width {
  max-width: unset;
}
@media (min-width: 960px) {
  .main-container:not(.full-width) {
    width: 87%;
  }
}
@media (min-width: 1264px) {
  .main-container:not(.full-width) {
    width: 83%;
  }
}
</style>
