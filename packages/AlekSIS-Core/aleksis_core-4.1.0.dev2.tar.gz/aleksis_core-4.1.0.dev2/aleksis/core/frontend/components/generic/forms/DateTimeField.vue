<script setup>
import DateField from "./DateField.vue";
import TimeField from "./TimeField.vue";

import { defineModel, defineProps, computed } from "vue";
import { DateTime } from "luxon";

const modelValue = defineModel({ type: String });
const { label, min, max, hideTime } = defineProps({
  label: {
    type: String,
    required: false,
    default: undefined,
  },
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
  hideTime: {
    type: Boolean,
    required: false,
    default: false,
  },
});

const date = computed({
  get() {
    if (modelValue.value) {
      return modelValue.value;
    }
    return undefined;
  },
  set(value) {
    let newDateTime = modelValue.value;

    newDateTime = newDateTime.set({
      year: value.year,
      month: value.month,
      day: value.day,
    });

    modelValue.value = newDateTime;
  },
});

const time = computed({
  get() {
    if (modelValue.value) {
      return modelValue.value.toFormat("HH:mm");
    }
    return undefined;
  },
  set(value) {
    let newDateTime = modelValue.value;

    const time = DateTime.fromISO(value);

    newDateTime = newDateTime.set({ hour: time.hour, minute: time.minute });

    modelValue.value = newDateTime;
  },
});
const minDT = computed(() => {
  return DateTime.fromISO(min);
});

const minDate = computed(() => {
  return minDT.value;
});

const minTime = computed(() => {
  if (modelValue.value && modelValue.value.hasSame(minDT.value, "day")) {
    return minDT.value.toFormat("HH:mm");
  } else {
    return undefined;
  }
});

const maxDT = computed(() => {
  return DateTime.fromISO(max);
});

const maxDate = computed(() => {
  return maxDT.value;
});
const maxTime = computed(() => {
  if (modelValue.value && modelValue.value.hasSame(maxDT.value, "day")) {
    return maxDT.value.toFormat("HH:mm");
  } else {
    return undefined;
  }
});
</script>

<template>
  <div>
    <v-row>
      <v-col class="py-0">
        <div>{{ label }}</div>
      </v-col>
    </v-row>
    <v-row>
      <v-col :cols="hideTime ? 12 : 7">
        <date-field
          v-model="date"
          v-bind="{ ...$attrs }"
          :label="$t('forms.date_time.date')"
          :min="minDate"
          :max="maxDate"
        />
      </v-col>
      <v-col cols="5" v-if="!hideTime">
        <time-field
          v-model="time"
          v-bind="{ ...$attrs }"
          :label="$t('forms.date_time.time')"
          :min="minTime"
          :max="maxTime"
        />
      </v-col>
    </v-row>
  </div>
</template>

<style scoped></style>
