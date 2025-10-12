<script setup>
import { computed } from "vue";
import Field from "../crud/form/Field.vue";
import { generateField } from "../../../composables/crud/useObjectForm.js";

const props = defineProps({
  items: {
    type: Object,
    required: true,
  },
});
const actualField = computed(() => generateField(props.items));
</script>

<template>
  <field :field="actualField" multiple />
</template>
