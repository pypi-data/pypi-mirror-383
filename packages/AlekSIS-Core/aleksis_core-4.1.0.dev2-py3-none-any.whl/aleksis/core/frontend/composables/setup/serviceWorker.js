import { ref, onMounted } from "vue";

/**
 * Vue composable to register the PWA service worker once the main
 * component gets ready.
 */
export function useServiceWorker() {
  const updateSW = ref(undefined);
  const offlineReady = ref(false);
  const needRefresh = ref(false);

  onMounted(async () => {
    try {
      const { registerSW } = await import("virtual:pwa-register");

      updateSW.value = registerSW({
        onOfflineReady() {
          offlineReady.value = true;
          console.log("PWA is offline-ready.");
        },
        onNeedRefresh() {
          needRefresh.value = true;
          console.log("PWA needs to be refreshed.");
        },
        onRegisteredSW(swUrl, r) {
          r &&
            setInterval(
              async () => {
                if (!(!r.installing && navigator)) return;

                if ("connection" in navigator && !navigator.onLine) return;

                const resp = await fetch(swUrl, {
                  cache: "no-store",
                  headers: {
                    cache: "no-store",
                    "cache-control": "no-cache",
                  },
                });

                if (resp?.status === 200) await r.update();
              },
              60 * 60 * 1000,
            );
        },
        onRegisterError(e) {
          console.log("Error while installing PWA: " + e);
        },
      });
    } catch {
      console.log("PWA disabled.");
    }
  });

  function updateServiceWorker() {
    offlineReady.value = false;
    needRefresh.value = false;
    updateSW.value && updateSW.value(true);
  }

  return {
    needRefresh,
    updateServiceWorker,
  };
}
