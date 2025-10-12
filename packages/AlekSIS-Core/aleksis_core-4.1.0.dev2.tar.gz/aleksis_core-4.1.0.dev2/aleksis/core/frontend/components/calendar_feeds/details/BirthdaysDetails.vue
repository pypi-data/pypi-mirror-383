<template>
  <base-calendar-feed-details v-bind="$props" without-time>
    <template #description="{ selectedEvent }">
      <v-divider />
      <v-card-text>
        <span>
          <v-icon class="mr-2">mdi-cake-variant-outline</v-icon>
          {{ $d($parseISODate(selectedEvent.meta.date_of_birth)) }}
        </span>
      </v-card-text>
    </template>
  </base-calendar-feed-details>
</template>

<script>
import calendarFeedDetailsMixin from "../../../mixins/calendarFeedDetails.js";
import BaseCalendarFeedDetails from "../../calendar/BaseCalendarFeedDetails.vue";

export default {
  name: "BirthdaysDetails",
  components: { BaseCalendarFeedDetails },
  mixins: [calendarFeedDetailsMixin],
};
</script>
