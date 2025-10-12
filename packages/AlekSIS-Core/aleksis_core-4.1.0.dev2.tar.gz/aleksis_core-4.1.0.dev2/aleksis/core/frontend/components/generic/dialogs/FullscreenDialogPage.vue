<script setup>
import { useAppStore } from "../../../stores/appStore";

const appStore = useAppStore();
</script>

<script>
export default {
  name: "FullscreenDialogPage",
  props: {
    fullWidth: {
      type: Boolean,
      default: false,
    },
    dialogOnInitialRoute: {
      type: Boolean,
      default: false,
    },
    fallbackUrl: {
      type: [Object, String],
      default: null,
    },
  },
  methods: {
    handleClose() {
      this.$backOrElse(this.fallbackUrl);
    },
  },
  computed: {
    isDialog() {
      return (
        this.dialogOnInitialRoute ||
        this.$route.path !== this.$router.history._startLocation
      );
    },
    component() {
      return this.isDialog ? "v-dialog" : "v-sheet";
    },
  },
};
</script>

<template>
  <component
    :is="component"
    :value="true"
    fullscreen
    scrollable
    hide-overlay
    transition="dialog-bottom-transition"
    v-bind="$attrs"
  >
    <v-card elevation="0">
      <v-card-title v-if="isDialog" class="pa-0">
        <v-toolbar>
          <slot name="cancel">
            <dialog-close-button @click="handleClose" />
          </slot>

          <v-toolbar-title>
            <slot name="title">
              {{ appStore.toolbarTitle }}
            </slot>
          </v-toolbar-title>

          <v-spacer></v-spacer>

          <v-toolbar-items>
            <slot name="toolbarActions" :toolbar="true" />
          </v-toolbar-items>
        </v-toolbar>
      </v-card-title>

      <v-card-text>
        <div
          :class="{
            'main-container': isDialog,
            'pa-3': isDialog,
            'full-width': isDialog && ($route.meta.fullWidth ?? fullWidth),
          }"
        >
          <slot />
        </div>
      </v-card-text>

      <v-card-actions>
        <slot name="actions" :toolbar="false" />
      </v-card-actions>
    </v-card>
  </component>
</template>
