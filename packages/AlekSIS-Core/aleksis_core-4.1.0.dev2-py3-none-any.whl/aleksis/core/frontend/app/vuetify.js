/*
 * Configuration for Vuetify
 */

import { createVuetify } from "vuetify";
import { createVueI18nAdapter } from "vuetify/locale/adapters/vue-i18n";
import LuxonAdapter from "@date-io/luxon";
import { VCalendar } from "vuetify/labs/VCalendar";
import { VColorInput } from "vuetify/labs/VColorInput";
import { VDateInput } from "vuetify/labs/VDateInput";
import { useI18n } from "@/vue-i18n";
import "@/@mdi/font/css/materialdesignicons.css";
import { aliases } from "vuetify/iconsets/mdi";
import "vuetify/_styles.css";
import "vuetify/_settings.css";
import "vuetify/_tools.css";
import i18n from "./i18n";

export const vuetifyOpts = {
  icons: {
    aliases: {
      ...aliases,
      cancel: "mdi-close",
      delete: "mdi-close", // Not a trashcan due to vuetify using this icon inside chips for closing etc.
      deleteContent: "mdi-delete-outline",
      success: "mdi-check",
      info: "mdi-information-outline",
      warning: "mdi-alert-outline",
      error: "mdi-alert-octagon-outline",
      prev: "mdi-chevron-left",
      next: "mdi-chevron-right",
      checkboxOn: "mdi-checkbox-marked-outline",
      checkboxIndeterminate: "mdi-minus-box-outline",
      edit: "mdi-pencil-outline",
      preferences: "mdi-cog-outline",
      save: "mdi-content-save-outline",
      search: "mdi-magnify",
      filterEmpty: "mdi-filter-outline",
      filterSet: "mdi-filter",
      send: "mdi-send-outline",
      holidays: "mdi-calendar-weekend-outline",
      home: "mdi-home-outline",
      groupType: "mdi-shape-outline",
      role: "mdi-badge-account-horizontal-outline",
      print: "mdi-printer-outline",
      schoolTerm: "mdi-calendar-range-outline",
      updatePwa: "mdi-update",
      dashboardWidgetOff: "mdi-dots-horizontal-circle-outline",
      dashboardWidgetReady: "mdi-circle-off-outline",
      dashboardWidgetBroken: "mdi-alert-circle-outline",
      dashboardWidgetOn: "mdi-check-circle-outline",
    },
  },
};

export default createVuetify({
  lang: {
    current: "en",
    t: (key, ...params) => i18n.t(key, params),
  },
  locale: {
    adapter: createVueI18nAdapter({ i18n, useI18n }),
  },
  components: {
    VCalendar,
    VColorInput,
    VDateInput,
  },
  date: {
    adapter: LuxonAdapter,
  },
  theme: {
    defaultTheme: "system",
  },
  ...vuetifyOpts,
});
