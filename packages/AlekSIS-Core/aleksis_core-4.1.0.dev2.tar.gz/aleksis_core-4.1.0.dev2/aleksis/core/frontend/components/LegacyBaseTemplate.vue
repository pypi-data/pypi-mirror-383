<!--
  Base component to load legacy views from Django.

  It loads the legacy view into an iframe and attaches some utility
  code to it. The legacy application and the new Vue application can
  communicate with each other through a message channel.

  This helps during the migration from the pure SSR Django application
  in AlekSIS 2.x to the pure Vue and GraphQL based application.
  It will be removed once legacy view get unsupported.
-->

<template>
  <message-box
    v-if="
      !byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate
    "
    type="error"
  >
    {{ $t("legacy.unworthy") }}
  </message-box>
  <iframe
    v-else
    :src="iFrameSrc"
    :height="iFrameHeight + 'px'"
    class="iframe-fullsize"
    ref="contentIFrame"
  ></iframe>
</template>

<script setup>
import { useAppStore } from "../stores/appStore";
import { useGoTo } from "vuetify";
import { computed, defineProps, watch, ref, onMounted } from "vue";
import { useRoute, useRouter } from "@/vue-router";
import { useLegacyBaseTemplate } from "../composables/app/legacyBaseTemplate";

const appStore = useAppStore();

defineProps({
  byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate:
    {
      type: Boolean,
      required: true,
    },
});

const route = useRoute();
const router = useRouter();

const iFrameHeight = ref(0);
const iFrameSrc = ref(undefined);
const contentIFrame = ref();

const goTo = useGoTo();

const { isLegacyBaseTemplate } = useLegacyBaseTemplate();

const queryString = computed(() => {
  let qs = [];
  for (const [param, value] of Object.entries(route.query)) {
    qs.push(`${param}=${encodeURIComponent(value)}`);
  }
  return "?" + qs.join("&");
});

function getIFrameURL() {
  const location = contentIFrame.value.contentWindow.location;
  const url = new URL(location);
  return url;
}

/** Handle iframe data after inner page loaded */
function load() {
  // Write new location of iframe back to Vue Router
  const path = getIFrameURL().pathname.replace(/^\/django/, "");
  const pathWithQueryString = path + encodeURI(getIFrameURL().search);
  const routePath =
    path.charAt(path.length - 1) === "/" &&
    route.path.charAt(path.length - 1) !== "/"
      ? route.path + "/"
      : route.path;
  if (path !== routePath) {
    router.push(pathWithQueryString);
  }

  // Show loader if iframe starts to change its content, even if the $route stays the same
  contentIFrame.value.contentWindow.onpagehide = () => {
    if (isLegacyBaseTemplate.value) {
      appStore.setContentLoading(true);
    }
  };

  // Write title of iframe to SPA window
  const title = contentIFrame.value.contentWindow.document.title;
  appStore.setPageTitle(title);
  contentIFrame.value.title = title;

  // Adapt height of IFrame according to the height of its contents once and observe height changes
  if (
    contentIFrame.value.contentDocument &&
    contentIFrame.value.contentDocument.body
  ) {
    iFrameHeight.value = contentIFrame.value.contentDocument.body.scrollHeight;
    new ResizeObserver(() => {
      if (
        contentIFrame.value &&
        contentIFrame.value.contentDocument &&
        contentIFrame.value.contentDocument.body
      ) {
        iFrameHeight.value =
          contentIFrame.value.contentDocument.body.scrollHeight;
      }
    }).observe(contentIFrame.value.contentDocument.body);
  }

  appStore.contentLoading = false;
}

watch(route, (newRoute) => {
  // Show loading animation once route changes
  appStore.contentLoading = true;

  // Only reload iFrame content when navigation comes from outsite the iFrame
  const path = getIFrameURL().pathname.replace(/^\/django/, "");
  const routePath =
    path.charAt(path.length - 1) === "/" &&
    newRoute.path.charAt(path.length - 1) !== "/"
      ? newRoute.path + "/"
      : newRoute.path;
  // If the current iFrame path does not start with the /django prefix – which should not be the case – add it
  if (path !== routePath || !getIFrameURL().pathname.startsWith("/django")) {
    contentIFrame.value.contentWindow.location =
      "/django" + route.path + queryString.value;
  } else {
    appStore.contentLoading = false;
  }

  // Scroll to top only when route changes to not affect form submits etc.
  // A small duration to avoid flashing of the UI
  goTo(0, { duration: 10 });
});

onMounted(() => {
  contentIFrame.value.addEventListener("load", () => {
    load();
  });
  iFrameSrc.value = "/django" + route.path + queryString.value;
});
</script>

<style scoped>
.iframe-fullsize {
  border: 0;
  width: calc(100% + 24px);
  margin: -12px;
}
</style>
