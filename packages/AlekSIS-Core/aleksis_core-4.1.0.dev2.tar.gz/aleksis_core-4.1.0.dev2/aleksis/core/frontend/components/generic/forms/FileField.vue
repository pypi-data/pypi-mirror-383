<template>
  <div>
    <v-file-input
      v-model="modelValue"
      :label="$attrs.label"
      :rules="$attrs.rules"
      :clearable="false"
      persistent-hint
      :hint="hint"
    >
      <template #append>
        <icon-button
          v-if="showClear"
          @click.stop="clearOrDelete"
          icon-text="$clear"
          i18n-key="actions.clear"
        />

        <v-expand-x-transition>
          <div
            v-show="(!modelValue && initialState?.url) || showDelete"
            class="d-flex justify-center align-center"
          >
            <div v-if="!modelValue && initialState?.url" class="mr-1">
              <slot name="append-outer" :file-url="initialState?.url" />
            </div>
            <icon-button
              v-if="showDelete"
              @click.stop="clearOrDelete"
              icon-text="$deleteContent"
              i18n-key="actions.delete"
            />
          </div>
        </v-expand-x-transition>
      </template>
    </v-file-input>
  </div>
</template>

<script setup>
import { defineModel, ref, useAttrs, watch, computed } from "vue";
import { useI18n } from "../../../composables/app/useI18n";
const { t } = useI18n();

const modelValue = defineModel({ type: [File, Object] });
const initialState = ref(undefined);
const attrs = useAttrs();

watch(
  modelValue.value,
  (newValue) => {
    if (initialState.value === undefined) {
      initialState.value = newValue;
    }
  },
  {
    deep: true,
    immediate: true,
  },
);

function clearOrDelete() {
  if (
    modelValue.value instanceof File &&
    modelValue.value != initialState.value
  ) {
    modelValue.value = undefined;
  } else if (initialState.value) {
    modelValue.value = null;
    initialState.value = undefined;
  }
}

const showClear = computed(() => {
  if (Object.hasOwn(attrs, "clearable") && !attrs.clearable) {
    return false;
  }
  return modelValue.value instanceof File;
});

const showDelete = computed(() => {
  if (Object.hasOwn(attrs, "clearable") && !attrs.clearable) {
    return false;
  }
  return (
    !(modelValue.value instanceof File) &&
    !!initialState.value &&
    initialState.value?.name
  );
});
const hint = computed(() => {
  if (!(initialState.value instanceof File) && initialState.value?.name) {
    return t("forms.file.hint", {
      fileName: initialState.value?.name,
    });
  }
  return attrs.hint;
});
</script>

<style scoped></style>
