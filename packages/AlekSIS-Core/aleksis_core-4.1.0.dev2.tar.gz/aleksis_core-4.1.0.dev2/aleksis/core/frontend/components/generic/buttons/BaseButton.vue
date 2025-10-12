<template>
  <v-btn
    v-bind="{ ...$props, ...$attrs }"
    :variant="compVariant"
    :aria-label="$t(i18nKey)"
    ref="btn"
  >
    <slot>
      <v-icon v-if="iconText" :start="!icon">{{ iconText }}</v-icon>
      <span v-if="!icon">{{ $t(i18nKey) }}</span>
    </slot>
    <v-tooltip
      location="bottom"
      :disabled="!icon && !forceTooltip"
      eager
      :activator="$refs.btn"
    >
      <span v-if="forceTooltip || icon">{{ $t(i18nKey) }}</span>
    </v-tooltip>
  </v-btn>
</template>

<script>
import { VBtn } from "@/vuetify/lib/components/VBtn";

export default {
  name: "BaseButton",
  inheritAttrs: true,
  extends: VBtn,
  props: {
    i18nKey: {
      type: String,
      required: true,
    },
    iconText: {
      type: String,
      required: false,
      default: undefined,
    },
    /**
     * Iconify the button.
     * Rund button that shows only the icon.
     */
    icon: {
      type: Boolean,
      required: false,
      default: false,
    },
    forceTooltip: {
      type: Boolean,
      required: false,
      default: false,
    },
    outlined: {
      type: Boolean,
      required: false,
      default: undefined,
    },
    text: {
      type: Boolean,
      required: false,
      default: undefined,
    },
  },
  computed: {
    compVariant() {
      if (this.outlined) {
        console.warn(
          "[base-button] Deprecated: Use variant='outlined' instead of outlined",
        );
        return "outlined";
      }
      if (this.text) {
        console.warn(
          "[base-button] Deprecated: Use variant='text' instead of text",
        );
        return "text";
      }
      if (this.outlined === false || this.text === false) {
        console.warn(
          "[base-button] Deprecated: Use variant prop instead of outlined or text",
        );
        return undefined;
      }

      return this.$attrs.variant || this.variant;
    },
  },
};
</script>

<style scoped></style>
