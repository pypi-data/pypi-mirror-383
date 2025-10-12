<template>
  <v-fab
    v-bind="$props"
    style="transform: none"
    fab
    size="large"
    app
    location="right bottom"
    :order="0"
    :icon="iconText"
    :aria-label="$t(i18nKey)"
  >
    <slot />
  </v-fab>
</template>

<script>
import { VFab } from "@/vuetify/lib/components/VFab";

export default {
  name: "FabButton",
  extends: VFab,
  props: {
    iconText: {
      type: String,
      required: true,
    },
    i18nKey: {
      type: String,
      required: true,
    },
  },
};
</script>
