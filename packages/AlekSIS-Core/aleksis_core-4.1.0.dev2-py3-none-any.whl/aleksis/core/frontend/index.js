/*
 * Main entrypoint of AlekSIS0-Core.
 *
 * This script sets up all necessary app plugins and defines the app app.
 */

import { createApp, h, provide } from "vue";
import { createPinia } from "@/pinia";
import VueApolloComponents from "@vue/apollo-components";
import VueCookies from "@/vue-cookies";
import draggableGrid from "@/vue-draggable-grid/dist/vue-draggable-grid";
import "@/vue-draggable-grid/dist/vue-draggable-grid.css";
import { createRulesPlugin } from "vuetify/labs/rules";

// All of these imports yield plugin objects to be passed to the app instance
import vuetify from "./app/vuetify.js";
import i18n from "./app/i18n.js";
import router from "./app/router.js";
import apollo, { apolloClient, DefaultApolloClient } from "./app/apollo.js";
import { useSentry } from "./app/sentry.js";

import AleksisVue from "./plugins/aleksis.js";

console.info("🎒 Welcome to AlekSIS®, the Free School Information System!");
console.info(
  "AlekSIS® is Free Software, licenced under the EUPL, version 1.2 or later, by Teckids e.V. (Bonn, Germany)",
);

// Parent component rendering the UI and all features outside the specific pages
import App from "./components/app/App.vue";

const app = createApp({
  setup() {
    provide(DefaultApolloClient, apolloClient);
  },
  render: () => h(App),
  data: () => ({
    showCacheAlert: false,
    invalidation: false,
    frequentCeleryPolling: false,
    activeSchoolTerm: null,
  }),
});

useSentry(app, router);

// Install VueI18n before AleksisVue to allow overriding of $d
// to make it compatible with Luxon
app.use(VueCookies);
app.use(i18n);

const lang = app.$cookies.get("django_language") || navigator.language || "en";
i18n.global.locale = lang;

// Install Pinia before AleksisVue to allow it to use the store
const pinia = createPinia();
app.use(pinia);

// Install the AleksisVue plugin first and let it do early setup
app.use(AleksisVue);
app.$registerGlobalComponents();

// Third-party plugins
app.use(draggableGrid);
app.use(vuetify);
vuetify.locale.current = lang;
app.use(createRulesPlugin({}, vuetify.locale));
app.use(router);

app.use(apollo);
app.use(VueApolloComponents);

// Late setup for some plugins handed off to out AleksisVue plugin
app.$setupNavigationGuards(router);
app.$loadVuetifyMessages(i18n.global);
app.$loadAppMessages(i18n.global);

// Finally mount app
app.mount("#app");
