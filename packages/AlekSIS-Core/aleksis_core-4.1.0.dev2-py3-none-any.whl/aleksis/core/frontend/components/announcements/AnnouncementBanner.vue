<script setup>
import { defineProps, ref } from "vue";
import MobileFullscreenDialog from "../generic/dialogs/MobileFullscreenDialog.vue";
import BaseButton from "../generic/buttons/BaseButton.vue";
import DialogCloseButton from "../generic/buttons/DialogCloseButton.vue";

defineProps({
  announcement: {
    type: Object,
    required: true,
  },
});

const dialogMode = ref(false);
</script>

<template>
  <v-banner
    v-bind="$attrs"
    color="warning"
    icon="mdi-bullhorn-variant-outline"
    lines="one"
  >
    <strong>{{ announcement.title }}</strong>

    <mobile-fullscreen-dialog
      v-model="dialogMode"
      hide-actions
      :close-button="false"
    >
      <template #title>
        <div class="d-flex align-center full-width">
          <v-icon color="primary" size="large" class="mr-2">
            mdi-bullhorn-variant-outline
          </v-icon>
          {{ announcement.title }}
          <v-spacer />
          <dialog-close-button @click="dialogMode = false" class="ml-2" />
        </div>
      </template>
      <template #content>
        <p>{{ announcement.description }}</p>

        <small
          >{{
            $d($parseISODate(announcement.datetimeStart), "shortDateTime")
          }}–{{
            $d($parseISODate(announcement.datetimeEnd), "shortDateTime")
          }}</small
        >
      </template>
    </mobile-fullscreen-dialog>

    <template #actions>
      <base-button text i18n-key="actions.more" @click="dialogMode = true" />
    </template>
  </v-banner>
</template>
