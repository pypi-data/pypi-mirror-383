<template>
  <base-calendar-feed-event-bar v-bind="$props" />
</template>

<script>
import calendarFeedEventBarMixin from "../../mixins/calendarFeedEventBar.js";
import BaseCalendarFeedEventBar from "./BaseCalendarFeedEventBar.vue";

export default {
  name: "GenericCalendarFeedEventBar",
  components: { BaseCalendarFeedEventBar },
  mixins: [calendarFeedEventBarMixin],
};
</script>
