<template>
  <v-list v-model:selected="model" select-strategy="leaf">
    <v-list-item
      v-for="calendarFeed in calendarFeeds"
      :key="calendarFeed.name"
      :value="calendarFeed.name"
      :tabindex="-1"
      :title="calendarFeed.verboseName"
    >
      <template #prepend="{ isSelected, select }">
        <v-checkbox-btn
          :model-value="isSelected"
          @update:model-value="select"
          :color="calendarFeed.color"
          class="focusable"
        ></v-checkbox-btn>
      </template>

      <template #append>
        <v-avatar v-if="calendarFeed.componentType === 'todo'">
          <v-icon> mdi-checkbox-multiple-marked-circle-outline </v-icon>
        </v-avatar>

        <button-menu
          icon-only
          variant="icon"
          icon="mdi-dots-vertical"
          text-translation-key="actions.more_actions"
        >
          <v-list-item :href="calendarFeed.url">
            <template #prepend>
              <v-icon>mdi-calendar-export</v-icon>
            </template>
            <v-list-item-title>
              {{ $t("calendar.download_ics") }}
            </v-list-item-title>
          </v-list-item>
        </button-menu>
      </template>
    </v-list-item>
  </v-list>
</template>

<script setup>
import { defineModel, defineProps } from "vue";

defineProps({
  calendarFeeds: {
    type: Array,
    required: true,
  },
});

const model = defineModel({
  type: Array,
  required: true,
});
</script>
