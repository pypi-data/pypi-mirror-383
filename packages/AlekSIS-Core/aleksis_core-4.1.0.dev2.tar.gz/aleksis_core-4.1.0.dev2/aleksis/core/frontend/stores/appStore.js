import { defineStore } from "@/pinia";
import { ref } from "vue";
import { useRoute } from "@/vue-router";
import i18n from "../app/i18n";

export const useAppStore = defineStore("appInfo", () => {
  const pageBaseTitle = ref("AlekSIS®");
  const toolbarTitle = ref("AlekSIS®");

  const whoAmI = ref(null);

  const offline = ref(false);
  const maintenance = ref(false);
  const backgroundActive = ref(true);

  const snackbarItems = ref([]);

  const contentLoading = ref(false);

  function setPageBaseTitle(newBaseTitle) {
    pageBaseTitle.value = newBaseTitle;
  }

  function setContentLoading(loading) {
    contentLoading.value = loading;
  }

  /**
   * Set the (browser) page title.
   *
   * This will automatically add the base title discovered at app loading time.
   *
   * @param {string} title Specific title to set, or null.
   * @param {Object} route Route to discover title from, or null.
   */
  function setPageTitle(title, route) {
    let titleParts = [];

    if (title) {
      titleParts.push(title);
    } else {
      if (!route) {
        route = useRoute();
      }
      if (route.meta.titleKey) {
        titleParts.push(i18n.global.t(route.meta.titleKey));
      }
    }

    titleParts.push(pageBaseTitle.value);
    const newTitle = titleParts.join(" – ");
    console.debug(`Setting page title: ${newTitle}`);
    document.title = newTitle;
  }

  /**
   * Set the toolbar title visible on the page.
   *
   * This will automatically add the base title discovered at app loading time.
   *
   * @param {string|null} title Specific title to set, or null.
   * @param {Object|null} route Route to discover title from, or null.
   */
  function setToolbarTitle(title, route) {
    let newTitle;

    if (title) {
      newTitle = title;
    } else {
      if (!route) {
        route = useRoute();
      }
      if (route.meta.toolbarTitle) {
        newTitle = i18n.global.t(route.meta.toolbarTitle);
      }
    }

    newTitle = newTitle || pageBaseTitle.value;
    console.debug(`Setting toolbar title: ${newTitle}`);
    toolbarTitle.value = newTitle;
  }

  return {
    contentLoading,
    setContentLoading,
    pageBaseTitle,
    setPageBaseTitle,
    setPageTitle,
    toolbarTitle,
    setToolbarTitle,
    offline,
    maintenance,
    snackbarItems,
    backgroundActive,
    whoAmI,
  };
});
