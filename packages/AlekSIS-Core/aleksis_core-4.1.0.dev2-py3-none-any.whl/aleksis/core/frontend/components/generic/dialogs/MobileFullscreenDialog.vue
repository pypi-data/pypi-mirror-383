<script setup>
import { defineModel } from "vue";

defineProps({
  maxWidth: {
    type: [String, Number],
    required: false,
    default: "600px",
  },
  closeButton: {
    type: Boolean,
    required: false,
    default: true,
  },
  hideActions: {
    type: Boolean,
    required: false,
    default: false,
  },
});

const dialogMode = defineModel("dialogMode", { type: Boolean });
</script>

<template>
  <v-dialog
    v-model="dialogMode"
    :fullscreen="$vuetify.display.xs"
    :scrim="false"
    :max-width="maxWidth"
  >
    <template #activator="activator">
      <slot name="activator" v-bind="activator"></slot>
    </template>
    <template #default>
      <slot>
        <v-card class="d-flex flex-column">
          <v-card-title class="d-flex align-center">
            <slot name="title"></slot>
            <v-spacer v-if="closeButton" />
            <dialog-close-button
              v-if="closeButton"
              @click="dialogMode = false"
            />
          </v-card-title>
          <v-card-text>
            <slot name="content"></slot>
          </v-card-text>
          <v-spacer />
          <v-divider />
          <v-card-actions v-if="!hideActions">
            <slot name="actionsLeft"></slot>
            <v-spacer></v-spacer>
            <slot name="actions"></slot>
          </v-card-actions>
        </v-card>
      </slot>
    </template>
  </v-dialog>
</template>
