<script setup>
const props = defineProps({
  value: {
    type: Array,
    required: true,
  },
  objectSchema: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <component
    v-for="(obj, idx) in value"
    :key="idx"
    :is="props.objectSchema.items.displayComponent"
    :value="obj"
    :object-schema="props.objectSchema"
    class="mr-1"
  />
</template>
