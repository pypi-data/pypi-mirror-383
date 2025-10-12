<script setup>
import { defineModel, reactive } from "vue";

const modelValue = defineModel({ type: String });

const availableCalendarTypes = reactive([
  {
    type: "month",
    translationKey: "calendar.month",
    icon: "mdi-calendar-month-outline",
    iconActive: "mdi-calendar-month",
  },
  {
    type: "week",
    translationKey: "calendar.week",
    icon: "mdi-calendar-week-outline",
    iconActive: "mdi-calendar-week",
  },
  {
    type: "day",
    translationKey: "calendar.day",
    icon: "mdi-calendar-today-outline",
    iconActive: "mdi-calendar-today",
  },
]);
</script>

<template>
  <v-btn-toggle density="compact" mandatory v-model="modelValue" class="mx-2">
    <v-btn
      v-for="calendarType in availableCalendarTypes"
      :value="calendarType.type"
      :key="calendarType.type"
      :aria-label="$t(calendarType.translationKey)"
    >
      <v-icon v-if="$vuetify.display.smAndDown">{{
        calendarType.type === modelValue
          ? calendarType.iconActive
          : calendarType.icon
      }}</v-icon>
      <span class="hidden-sm-and-down">
        {{ $t(calendarType.translationKey) }}
      </span>
    </v-btn>
  </v-btn-toggle>
</template>
