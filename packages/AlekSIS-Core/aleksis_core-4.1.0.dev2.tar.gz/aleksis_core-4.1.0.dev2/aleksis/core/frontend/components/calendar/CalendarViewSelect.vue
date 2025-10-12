<script setup>
import { defineModel, reactive } from "vue";

const modelValue = defineModel({ type: String });
const availableCalendarViews = reactive([
  {
    type: "calendar",
    translationKey: "calendar.views.calendar",
    icon: "mdi-calendar-multiple",
    iconActive: "mdi-calendar-multiple",
  },
  {
    type: "todos",
    translationKey: "calendar.views.todos",
    icon: "mdi-checkbox-multiple-marked-circle-outline",
    iconActive: "mdi-checkbox-multiple-marked-circle-outline",
  },
]);
</script>

<template>
  <v-btn-toggle density="compact" mandatory v-model="modelValue" class="mx-2">
    <v-btn
      v-for="calendarView in availableCalendarViews"
      :value="calendarView.type"
      :key="calendarView.type"
      :aria-label="$t(calendarView.translationKey)"
    >
      <v-icon v-if="$vuetify.display.smAndDown">{{
        calendarView.type === modelValue
          ? calendarView.iconActive
          : calendarView.icon
      }}</v-icon>
      <span class="hidden-sm-and-down">
        {{ $t(calendarView.translationKey) }}
      </span>
    </v-btn>
  </v-btn-toggle>
</template>
