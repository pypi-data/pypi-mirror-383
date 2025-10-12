<template>
  <span>
    <span v-if="value">{{ $t(`weekdays.${value}`) }}</span>
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
