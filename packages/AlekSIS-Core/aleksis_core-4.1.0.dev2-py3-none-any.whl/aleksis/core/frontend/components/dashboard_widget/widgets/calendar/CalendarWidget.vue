<script>
import widgetMixin from "../widgetMixin";
import Calendar from "../../../calendar/Calendar.vue";

export default {
  name: "CalendarWidget",
  components: { Calendar },
  mixins: [widgetMixin],
  computed: {
    feeds() {
      return JSON.parse(this.context).selected_calendars.map((calName) => ({
        name: calName,
      }));
    },
  },
};
</script>

<template>
  <v-card>
    <v-card-title>
      {{ widget.title }}
    </v-card-title>
    <v-card-text>
      <calendar
        :calendar-feeds="feeds"
        ref="calendar"
        scroll-target="current"
        type="day"
      />
    </v-card-text>
  </v-card>
</template>
