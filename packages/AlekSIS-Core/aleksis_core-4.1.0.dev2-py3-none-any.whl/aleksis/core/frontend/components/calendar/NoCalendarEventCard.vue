<script>
export default {
  name: "NoCalendarEventCard",
  props: {
    titleKey: {
      type: String,
      required: false,
      default: "calendar.no_calendar_event_card.title",
    },
    descriptionKey: {
      type: String,
      required: false,
      default: "calendar.no_calendar_event_card.description",
    },
    selectButtonKey: {
      type: String,
      required: false,
      default: "calendar.no_calendar_event_card.select_button",
    },
    icon: {
      type: String,
      required: false,
      default: "mdi-calendar-question-outline",
    },
  },
  emits: ["selectCalendar"],
};
</script>

<template>
  <v-card
    class="full-height d-flex align-center justify-center py-10"
    v-bind="$attrs"
  >
    <div class="text-center">
      <v-icon color="secondary" size="60" class="mb-4"> {{ icon }} </v-icon>
      <div class="text-h5 text-grey-darken-2 mb-2">
        {{ $t(titleKey) }}
      </div>
      <div
        class="text-body-2 text-grey-darken-2"
        v-if="$vuetify.display.lgAndUp"
      >
        {{ $t(descriptionKey) }}
      </div>
      <div v-if="$vuetify.display.mdAndDown">
        <v-btn color="primary" @click="$emit('selectCalendar')" class="mt-4">
          {{ $t(selectButtonKey) }}
        </v-btn>
      </div>
    </div>
  </v-card>
</template>
