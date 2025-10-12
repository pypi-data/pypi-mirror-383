<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    transition="scale-transition"
    min-width="290"
    eager
  >
    <template #activator="{ props }">
      <v-text-field
        v-model="modelValue"
        v-bind="{ ...$attrs, ...props }"
        @click="handleClick"
        @focusin="handleFocusIn"
        @focusout="handleFocusOut"
        @click:clear="handleClickClear"
        placeholder="HH:MM[:SS]"
        @keydown.esc="menu = false"
        @keydown.enter="menu = false"
        :prepend-icon="prependIcon"
        :rules="mergedRules"
      ></v-text-field>
    </template>
    <v-time-picker
      v-model="modelValue"
      ref="picker"
      :min="limitSelectableRange ? min : ''"
      :max="limitSelectableRange ? max : ''"
      full-width
      format="24hr"
      @click:minute="menu = false"
    ></v-time-picker>
  </v-menu>
</template>

<script setup>
import { defineModel, defineProps, ref, computed } from "vue";
import { useI18n } from "../../../composables/app/useI18n";

const { t } = useI18n();

const modelValue = defineModel({ type: String });
const menu = ref(false);
const openDueToFocus = ref(true);

const { min, max, prependIcon, rules, limitSelectableRange } = defineProps({
  min: {
    type: String,
    required: false,
    default: undefined,
  },
  max: {
    type: String,
    required: false,
    default: undefined,
  },
  prependIcon: {
    type: String,
    required: false,
    default: undefined,
  },
  rules: {
    type: Array,
    required: false,
    default: () => [],
  },
  limitSelectableRange: {
    type: Boolean,
    required: false,
    default: true,
  },
});

const mergedRules = computed(() => {
  return [
    (v) =>
      !v ||
      /^([01]\d|2[0-3]):([0-5]\d)(:([0-5]\d))?$/.test(v) ||
      t("forms.errors.invalid_time"),
    ...rules,
  ];
});

function handleClickClear() {
  if (this.clearable) {
    modelValue.value = null;
  }
}
function handleClick() {
  menu.value = true;
  openDueToFocus.value = false;
}
function handleFocusIn() {
  openDueToFocus.value = true;
  menu.value = true;
}

function handleFocusOut(event) {
  if (openDueToFocus.value) menu.value = false;
  modelValue.value = event.target.value;
}
</script>

<style scoped></style>
