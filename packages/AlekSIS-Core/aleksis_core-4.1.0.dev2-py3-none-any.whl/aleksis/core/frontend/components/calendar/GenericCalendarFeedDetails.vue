<template>
  <base-calendar-feed-details v-bind="$props"> </base-calendar-feed-details>
</template>

<script>
import calendarFeedDetailsMixin from "../../mixins/calendarFeedDetails.js";
import BaseCalendarFeedDetails from "./BaseCalendarFeedDetails.vue";

export default {
  name: "GenericCalendarFeedDetails",
  components: { BaseCalendarFeedDetails },
  mixins: [calendarFeedDetailsMixin],
};
</script>
