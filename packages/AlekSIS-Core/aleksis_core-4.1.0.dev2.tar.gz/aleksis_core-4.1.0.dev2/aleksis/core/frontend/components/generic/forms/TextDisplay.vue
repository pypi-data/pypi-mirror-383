<template>
  <span v-if="value">{{ value }}</span>
  <span v-else>–</span>
</template>

<script setup>
import { defineProps } from "vue";

const { value } = defineProps({
  value: {
    type: [String, Number],
    default: undefined,
  },
});
</script>
