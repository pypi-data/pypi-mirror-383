import { computed } from "vue";
import { useRoute } from "@/vue-router";

export function useLegacyBaseTemplate() {
  const $route = useRoute();

  const matchedComponents = computed(() => {
    if ($route?.matched?.length > 0) {
      return $route.matched.map((route) => route.components?.default.__name);
    }
    return [];
  });

  const isLegacyBaseTemplate = computed(() => {
    return matchedComponents.value.includes("LegacyBaseTemplate");
  });

  return {
    isLegacyBaseTemplate,
  };
}
