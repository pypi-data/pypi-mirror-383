/*
 * Plugin to collect AlekSIS-specific app utilities.
 */

// aleksisAppImporter is a virtual module defined in Vite config
import { appMessages } from "aleksisAppImporter";
import aleksisMixin from "../mixins/aleksis.js";
import * as langs from "@/vuetify/lib/locale";
import { useAppStore } from "../stores/appStore";
import { useLegacyBaseTemplate } from "../composables/app/legacyBaseTemplate";
import { apolloClient } from "../app/apollo.js";

// Import all common generic components for use in all AlekSIS apps
// General stuff
import AvatarClickbox from "../components/generic/AvatarClickbox.vue";
import CalendarWithControls from "../components/calendar/CalendarWithControls.vue";
import ErrorPage from "../components/app/ErrorPage.vue";
import MessageBox from "../components/generic/MessageBox.vue";
import SmallContainer from "../components/generic/SmallContainer.vue";

// Layout
import DetailView from "../components/generic/DetailView.vue";
import ListView from "../components/generic/ListView.vue";

// Buttons
import BackButton from "../components/generic/BackButton.vue";
import ButtonMenu from "../components/generic/ButtonMenu.vue";
import CancelButton from "../components/generic/buttons/CancelButton.vue";
import CreateButton from "../components/generic/buttons/CreateButton.vue";
import DeleteButton from "../components/generic/buttons/DeleteButton.vue";
import DialogCloseButton from "../components/generic/buttons/DialogCloseButton.vue";
import EditButton from "../components/generic/buttons/EditButton.vue";
import FabButton from "../components/generic/buttons/FabButton.vue";
import FilterButton from "../components/generic/buttons/FilterButton.vue";
import IconButton from "../components/generic/buttons/IconButton.vue";
import PrimaryActionButton from "../components/generic/buttons/PrimaryActionButton.vue";
import SaveButton from "../components/generic/buttons/SaveButton.vue";
import SecondaryActionButton from "../components/generic/buttons/SecondaryActionButton.vue";

console.debug("Defining AleksisVue plugin");
const AleksisVue = {};

AleksisVue.install = function (app) {
  const appStore = useAppStore();
  /*
   * The browser title when the app was loaded.
   *
   * Thus, it is injected from Django in the vue_index template.
   */
  appStore.setPageBaseTitle(document.title);

  app.$aleksisFrontendSettings = JSON.parse(
    document.getElementById("frontend_settings").textContent,
  );

  /**
   * Register all global components that shall be reusable by apps.
   */
  app.$registerGlobalComponents = function () {
    const globalComponents = [
      AvatarClickbox,
      CalendarWithControls,
      ErrorPage,
      MessageBox,
      SmallContainer,
      DetailView,
      ListView,
      BackButton,
      ButtonMenu,
      CancelButton,
      CreateButton,
      DeleteButton,
      DialogCloseButton,
      EditButton,
      FabButton,
      FilterButton,
      IconButton,
      PrimaryActionButton,
      SaveButton,
      SecondaryActionButton,
    ];

    globalComponents.forEach((component) => {
      app.component(component.name, component);
    });
  };

  /**
   * Set the page title.
   *
   * This will automatically add the base title discovered at app loading time.
   *
   * @param {string} title Specific title to set, or null.
   * @param {Object} route Route to discover title from, or null.
   */
  app.config.globalProperties.$setPageTitle = function (title, route) {
    console.warn(
      "$setPageTitle is deprecated, use appStore.setPageTitle instead",
    );
    appStore.setPageTitle(title, route);
  };

  /**
   * Set the toolbar title visible on the page.
   *
   * This will automatically add the base title discovered at app loading time.
   *
   * @param {string} title Specific title to set, or null.
   * @param {Object} route Route to discover title from, or null.
   */
  app.config.globalProperties.$setToolBarTitle = function (title, route) {
    console.warn(
      "$setToolBarTitle is deprecated, use appStore.setToolbarTitle instead",
    );
    appStore.setToolbarTitle(title, route);
  };

  /**
   * Get base title defined by current Instance
   * @return {string} Title as defined in site preferences
   */
  app.config.globalProperties.$getBaseTitle = function () {
    console.warn("$getBaseTitle is deprecated, use app.pageBaseTitle instead");
    return app.$pageBaseTitle;
  };

  /**
   * Load i18n messages from all known AlekSIS apps.
   */
  app.$loadAppMessages = function (i18n) {
    for (const messages of Object.values(appMessages)) {
      for (let locale in messages) {
        i18n.mergeLocaleMessage(locale, messages[locale]);
      }
    }
  };

  /**
   * Load vuetifys built-in translations
   */
  app.$loadVuetifyMessages = function (i18n) {
    for (const [locale, messages] of Object.entries(langs)) {
      i18n.mergeLocaleMessage(locale, { $vuetify: messages });
    }
  };

  /**
   * Invalidate state and force reload from server.
   *
   * Mostly useful after the user context changes by login/logout/impersonate.
   */
  app.config.globalProperties.$invalidateState = function () {
    console.info("Invalidating application state");

    this.invalidation = true;

    apolloClient.resetStore().then(
      () => {
        console.info("GraphQL cache cleared");
        this.invalidation = false;
      },
      (error) => {
        console.error("Could not clear GraphQL cache:", error);
        this.invalidation = false;
      },
    );
  };

  /**
   * Add navigation guards to account for global loading state and page titles.
   */
  app.$setupNavigationGuards = function (router) {
    // eslint-disable-next-line no-unused-vars
    router.afterEach((to, from, next) => {
      console.debug("Setting new page title due to route change");
      appStore.setPageTitle(null, to);
      appStore.setToolbarTitle(null, to);
    });

    // eslint-disable-next-line no-unused-vars
    router.beforeEach((to, from, next) => {
      appStore.contentLoading = true;
      next();
    });

    // eslint-disable-next-line no-unused-vars
    router.afterEach((to, from) => {
      const { isLegacyBaseTemplate } = useLegacyBaseTemplate();

      if (isLegacyBaseTemplate.value) {
        // Skip resetting loading state for legacy pages
        // as they are probably not finished with loading yet
        // LegacyBaseTemplate will reset the loading state later
        return;
      }
      appStore.contentLoading = false;
    });

    // eslint-disable-next-line no-unused-vars
    router.beforeEach((to, from, next) => {
      if (from.meta.invalidate === "leave" || to.meta.invalidate === "enter") {
        console.debug("Route requests to invalidate state");
        app.config.globalProperties.$invalidateState();
      }
      next();
    });
  };

  /**
   * Activate frequent polling for celery task progress.
   *
   * This can be used to notify the frontend about a currently running task that
   * should be monitored more closely.
   *
   */
  app.config.globalProperties.$activateFrequentCeleryPolling = function () {
    console.debug("Activate frequent polling for Celery tasks");
    this.$root.frequentCeleryPolling = true;
  };

  // Add default behaviour for all components
  app.mixin(aleksisMixin);
};

export default AleksisVue;
