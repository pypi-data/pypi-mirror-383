<script setup>
import GroupChip from "../../group/GroupChip.vue";

defineProps({
  value: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <group-chip :group="value" />
</template>
