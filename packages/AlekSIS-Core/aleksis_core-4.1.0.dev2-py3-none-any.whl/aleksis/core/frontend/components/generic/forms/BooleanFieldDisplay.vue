<template>
  <v-switch inset :model-value="value" disabled />
</template>

<script setup>
import { defineProps } from "vue";

const { value } = defineProps({
  value: {
    type: Boolean,
    default: false,
  },
});
</script>
