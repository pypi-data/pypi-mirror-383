import { useQuery as useApolloQuery } from "@vue/apollo-composable";
import { computed, toValue } from "vue";
import { useAppStore } from "../../stores/appStore";

export function useQuery(document, variables = null, options = null) {
  const appStore = useAppStore();

  const computedOptions = computed(() => {
    const defaultOptions = {
      fetchPolicy: "cache-and-network",
    };

    const optionsValue = toValue(options) || {};

    let enabled = optionsValue.enabled;

    if (
      (!appStore.backgroundActive || appStore.offline) &&
      !!optionsValue.pollInterval
    ) {
      enabled = false;
    }

    return {
      ...defaultOptions,
      ...optionsValue,
      enabled: enabled,
    };
  });

  return useApolloQuery(document, variables, computedOptions);
}
