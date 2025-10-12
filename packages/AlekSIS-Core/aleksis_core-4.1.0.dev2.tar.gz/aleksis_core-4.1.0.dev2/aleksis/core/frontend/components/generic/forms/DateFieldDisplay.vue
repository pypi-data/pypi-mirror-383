<template>
  <span>
    <span v-if="value">{{ $d($parseISODate(value), "short") }}</span>
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
