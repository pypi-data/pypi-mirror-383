import { useRouter, useRoute } from "@/vue-router";
import { useAppStore } from "../../stores/appStore";
import { ref } from "vue";

/**
 * Vue composable containing code setting error 404 status.
 *
 * Only used by main App component, but factored out for readability.
 */
export const useError404 = function () {
  const router = useRouter();
  const route = useRoute();
  const appInfo = useAppStore();

  const isError404 = ref(false);

  function set404() {
    if (route.matched.length === 0) {
      isError404.value = true;
      appInfo.contentLoading = false;
    } else {
      isError404.value = false;
    }
  }

  function initRouterFor404() {
    router.isReady().then(set404);
    router.afterEach((to, from) => {
      set404();
    });
  }

  return {
    isError404,
    set404,
    initRouterFor404,
  };
};
