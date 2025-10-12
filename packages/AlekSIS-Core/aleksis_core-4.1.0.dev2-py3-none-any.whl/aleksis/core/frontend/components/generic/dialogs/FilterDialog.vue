<script setup>
import { ref, computed, reactive, defineModel, watch, defineExpose } from "vue";
import { convertCamelToSnake } from "../../../composables/crud/useObjectForm";
import MobileFullscreenDialog from "./MobileFullscreenDialog.vue";
import CancelButton from "../buttons/CancelButton.vue";
import SaveButton from "../buttons/SaveButton.vue";

const filters = defineModel({});
const props = defineProps({
  objectSchema: {
    type: Object,
    required: true,
  },
});

const internalFilters = ref({});

function save() {
  // Do not emit empty filters having a null value.
  filters.value = Object.fromEntries(
    Object.entries(internalFilters.value).filter(
      ([field, filter]) => filter !== null,
    ),
  );
}

function clearFilters() {
  internalFilters.value = {};
  filters.value = {};
}

defineExpose({ clearFilters });

function propsForField(field, accessor, defaultValue) {
  const realField =
    convertCamelToSnake(field) + (accessor ? "__" + accessor : "");
  if (
    [null, undefined].includes(internalFilters[realField]) &&
    !!defaultValue
  ) {
    // eslint-disable-next-line vue/no-mutating-props
    internalFilters.value[realField] = defaultValue;
  }
  return reactive({
    modelValue: computed(() => internalFilters.value[realField]),
    "onUpdate:modelValue": (filter) =>
      (internalFilters.value[realField] = filter),
    disableCreate: true, // default for ObjectField,
    label: props.objectSchema.properties[field].label,
  });
}

watch(filters.value, () => {
  internalFilters.value = filters.value;
});
</script>

<template>
  <mobile-fullscreen-dialog v-bind="$attrs" :close-button="false">
    <template #title>{{ $t("actions.filter") }}</template>

    <template #content>
      <form @submit.stop.prevent="save">
        <!-- @slot Insert a field for selecting a filter. -->
        <!-- This slot is required for the filter to work. -->
        <slot name="filters" :props-for-field="propsForField" />
      </form>
    </template>

    <template #actions>
      <cancel-button
        i18n-key="actions.clear_filters"
        @click="clearFilters"
      ></cancel-button>
      <save-button
        i18n-key="actions.filter"
        icon-text="$filterEmpty"
        @click="save"
      ></save-button>
    </template>
  </mobile-fullscreen-dialog>
</template>
