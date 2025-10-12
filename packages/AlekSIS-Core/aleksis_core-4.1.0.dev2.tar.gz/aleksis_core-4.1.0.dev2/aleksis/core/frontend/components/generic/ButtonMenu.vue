<template>
  <v-menu
    transition="slide-y-transition"
    :close-on-content-click="closeOnContentClick"
  >
    <template #activator="menu">
      <slot name="activator" v-bind="menu">
        <v-tooltip location="bottom" :disabled="!iconOnly">
          <template #activator="tooltip">
            <v-btn
              :variant="compVariant"
              v-bind="{ ...tooltip.props, ...menu.props, ...$attrs }"
              :aria-label="$t(textTranslationKey)"
              :prepend-icon="compPrependIcon"
              :icon="variant === 'icon'"
            >
              <v-icon v-if="iconOnly" center>
                {{ icon }}
              </v-icon>
              <span v-else>{{ $t(textTranslationKey) }}</span>
            </v-btn>
          </template>
          <span v-if="iconOnly">{{ $t(textTranslationKey) }}</span>
        </v-tooltip>
      </slot>
    </template>

    <v-list>
      <slot />
    </v-list>
  </v-menu>
</template>

<script>
export default {
  name: "ButtonMenu",
  props: {
    icon: {
      type: String,
      required: false,
      default: "mdi-dots-horizontal",
    },
    textTranslationKey: {
      type: String,
      required: true,
    },
    iconOnly: {
      type: Boolean,
      required: false,
      default: false,
    },
    closeOnContentClick: {
      type: Boolean,
      required: false,
      default: true,
    },
    outlined: {
      type: Boolean,
      default: undefined,
    },
    text: {
      type: Boolean,
      default: undefined,
    },
    variant: {
      type: String,
      required: false,
      default: "outlined",
    },
  },
  computed: {
    compVariant() {
      if (this.outlined === false) {
        console.warn(
          "[base-button] Deprecated: Use variant='text' instead of outlined='false'",
        );
        return "text";
      }
      if (this.text === false) {
        console.warn(
          "[base-button] Deprecated: Use variant='elevated' instead of text='false'",
        );
        return "elevated";
      }

      return this.variant;
    },
    compIcon() {
      return this.iconOnly ? this.icon : undefined;
    },
    compPrependIcon() {
      return this.iconOnly ? undefined : this.icon;
    },
  },
};
</script>

<style scoped></style>
