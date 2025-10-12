<script setup>
import Mascot from "../generic/mascot/Mascot.vue";
import PrimaryActionButton from "../generic/buttons/PrimaryActionButton.vue";
</script>

<template>
  <div
    class="d-flex justify-center align-center flex-column text-center"
    id="wrapper"
  >
    <mascot
      v-if="mascotType"
      :style="{ height: '50vh', width: '50vh' }"
      :type="mascotType"
      rotate
    />
    <h1 class="text-h2">{{ $t(shortErrorMessageKey) }}</h1>
    <div>{{ $t(longErrorMessageKey) }}</div>
    <primary-action-button
      color="secondary"
      :to="{ name: redirectRouteName, ...redirectRouteArgs }"
      v-if="!hideButton"
      :icon-text="redirectButtonIcon"
      :i18n-key="redirectButtonTextKey"
    />
  </div>
</template>

<script>
export default {
  name: "ErrorPage",
  props: {
    shortErrorMessageKey: {
      type: String,
      required: true,
    },
    longErrorMessageKey: {
      type: String,
      required: true,
    },
    redirectButtonTextKey: {
      type: String,
      required: true,
    },
    redirectRouteName: {
      type: String,
      required: true,
    },
    redirectRouteArgs: {
      type: Object,
      required: false,
      default: () => {},
    },
    redirectButtonIcon: {
      type: String,
      required: true,
    },
    hideButton: {
      type: Boolean,
      default: false,
      required: false,
    },
    mascotType: {
      type: String,
      required: false,
      default: "",
    },
  },
};
</script>

<style scoped>
#wrapper {
  min-height: 70vh;
  gap: 1em;
}
</style>
