import gqlPing from "../../components/app/ping.graphql";
import { useAppStore } from "../../stores/appStore";
import { useEventListener } from "../utils/domEvent";
import { useQuery } from "@vue/apollo-composable";
import { computed } from "vue";

/**
 * Composable for handling of offline state / background queries.
 *
 * This handles three scenarios:
 *   - The navigator reports that it is in offline mode
 *   - The global offline flag was set due to network errors from queries
 *   - The navigator reports the page to be invisible
 *
 * The main goal is to save bandwidth, energy and server load in error
 * conditions, or when the page is not in focus. This is achieved by a
 * fallback strategy, where all background queries are stopped in offline
 * state, and only a ping query is sent once the navigator reports itself
 * as online and the app gets into focus. Once this ping query is successful,
 * background activity is resumed.
 */
export function useOffline() {
  const appStore = useAppStore();

  function checkOfflineState() {
    const state = navigator.onLine && document.visibilityState === "visible";
    console.info("Resuming background activity:", state);
    appStore.backgroundActive = state;
  }

  useEventListener(window, "online", () => {
    console.info("Navigator changed status to online.");
    checkOfflineState();
  });

  useEventListener(window, "offline", () => {
    console.info("Navigator changed status to offline.");
    checkOfflineState();
  });

  useEventListener(document, "visibilitychange", () => {
    console.info("Visibility changed status to", document.visibilityState);
    checkOfflineState();
  });

  const enabled = computed(() => appStore.backgroundActive && appStore.offline);

  // Use apollo useQuery instead of the wrapper because this query should only run if online is true
  const { onResult } = useQuery(
    gqlPing,
    () => ({ payload: Date.now().toString() }),
    {
      pollInterval: 5000,
      enabled: enabled,
    },
  );

  onResult((result) => {
    if (result.data?.ping) {
      console.info("Ping successful, clearing offline state");
      appStore.offline = false;
    }
  });
}
