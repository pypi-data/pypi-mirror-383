<script setup>
import PersonChip from "../../person/PersonChip.vue";

defineProps({
  value: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <person-chip :person="value" />
</template>
