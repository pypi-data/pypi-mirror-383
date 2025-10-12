/*
 * Configuration for VueI18n
 */

import { createI18n } from "@/vue-i18n";
import dateTimeFormats from "./dateTimeFormats.js";

export const i18nOpts = {
  // Locale is overridden once the app is mounted
  locale: "en",
  fallbackLocale: "en",
  messages: {},
  datetimeFormats: dateTimeFormats,
};

const i18n = createI18n(i18nOpts);

export default i18n;
