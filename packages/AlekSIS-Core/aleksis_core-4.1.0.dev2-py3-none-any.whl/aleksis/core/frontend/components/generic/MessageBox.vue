<script>
export default {
  name: "MessageBox",
  // Due to this component being a wrapper to a v-alert, all props of this can be used (and overridden).
  extends: "v-alert",
};
</script>

<template>
  <v-alert border="start" variant="tonal" text v-bind="$attrs">
    <template #prepend>
      <slot name="prepend" />
    </template>
    <slot />
  </v-alert>
</template>
