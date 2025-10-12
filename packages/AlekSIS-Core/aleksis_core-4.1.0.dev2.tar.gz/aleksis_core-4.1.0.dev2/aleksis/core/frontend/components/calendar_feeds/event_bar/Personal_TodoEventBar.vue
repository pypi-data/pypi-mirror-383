<template>
  <base-calendar-feed-event-bar
    v-bind="$props"
    icon="mdi-checkbox-multiple-marked-circle-outline"
  />
</template>

<script>
import calendarFeedEventBarMixin from "../../../mixins/calendarFeedEventBar.js";
import BaseCalendarFeedEventBar from "../../calendar/BaseCalendarFeedEventBar.vue";

export default {
  name: "PersonalTodoEventBar",
  components: { BaseCalendarFeedEventBar },
  mixins: [calendarFeedEventBarMixin],
};
</script>
