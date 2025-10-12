<!-- schema & layout & editItem -> patch -->

<script setup>
import { useSlots, defineProps, defineEmits, watch, ref } from "vue";
import { useObjectForm } from "../../../composables/crud/useObjectForm.js";
import { objectFormProps } from "../../../composables/crud/useObjectFormProps.js";

const props = defineProps({
  ...objectFormProps,
});

const valid = ref(false);
const emit = defineEmits(["update:editItem", "patch", "save"]);

const slots = useSlots();
function onItemUpdate(item) {
  emit("update:editItem", item);
}
const { form, patch } = useObjectForm(
  props.objectSchema,
  props.objectLayout,
  props.editItem,
  slots,
  onItemUpdate,
);

watch([valid.value, patch.value], () => {
  if (valid.value === true) {
    emit("patch", patch.value);
  }
});
</script>

<template>
  <v-form v-model="valid" @submit.stop.prevent="emit('save')">
    <form.component v-bind="form.props" />
  </v-form>
</template>
