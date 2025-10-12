<template>
  <span>
    <secondary-action-button
      variant="text"
      v-if="value"
      :href="value.url"
      i18n-key="actions.view_file"
      target="_blank"
      :title="value.name"
    >
    </secondary-action-button>
    <span v-else>–</span>
  </span>
</template>

<script setup>
import { defineProps } from "vue";

const { value } = defineProps({
  value: {
    type: Object,
    default: undefined,
  },
});
</script>
