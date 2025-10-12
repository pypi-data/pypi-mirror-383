<script>
export default {
  name: "ActivatedChip",
  props: {
    activated: {
      type: Boolean,
      required: true,
    },
  },
};
</script>

<template>
  <v-chip right color="success" variant="outlined" v-if="activated">
    <v-icon start>mdi-check-circle-outline</v-icon>
    <slot name="activated">
      {{ $t("accounts.two_factor.activated") }}
    </slot>
  </v-chip>
  <v-chip right color="error" variant="outlined" v-else>
    <v-icon start>mdi-close-circle-outline</v-icon>
    <slot name="deactivated">
      {{ $t("accounts.two_factor.deactivated") }}
    </slot>
  </v-chip>
</template>

<style scoped></style>
