<template>
  <v-snackbar v-bind="$attrs">
    <slot />
    <template #actions="{ attrs }">
      <icon-button
        v-bind="attrs"
        @click="close()"
        icon-text="$close"
        i18n-key="actions.close"
      />
    </template>
  </v-snackbar>
</template>

<script>
export default {
  name: "ClosableSnackbar",
  extends: "v-snackbar",
  methods: {
    close() {
      this.$emit("input", false);
    },
  },
};
</script>

<style scoped></style>
