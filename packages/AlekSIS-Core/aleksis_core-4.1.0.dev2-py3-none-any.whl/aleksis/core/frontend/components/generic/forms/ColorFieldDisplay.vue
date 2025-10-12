<script setup>
const props = defineProps({
  value: {
    type: String,
    default: undefined,
  },
});
</script>

<template>
  <v-chip v-if="props.value" :color="props.value" variant="outlined">
    {{ props.value }}
  </v-chip>
  <span v-else>–</span>
</template>
