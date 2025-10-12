<template>
  <base-calendar-feed-event-bar
    v-bind="$props"
    icon="mdi-cake-variant-outline"
  />
</template>

<script>
import calendarFeedEventBarMixin from "../../../mixins/calendarFeedEventBar.js";
import BaseCalendarFeedEventBar from "../../calendar/BaseCalendarFeedEventBar.vue";

export default {
  name: "BirthdaysEventBar",
  components: { BaseCalendarFeedEventBar },
  mixins: [calendarFeedEventBarMixin],
};
</script>
