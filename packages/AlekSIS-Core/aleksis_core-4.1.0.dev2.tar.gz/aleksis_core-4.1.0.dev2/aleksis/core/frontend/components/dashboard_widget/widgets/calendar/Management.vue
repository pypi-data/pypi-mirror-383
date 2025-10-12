<script>
import managementMixin from "../managementMixin";
import { updateCalendarWidgets } from "../../management/dashboardWidgetManagement.graphql";
import { calendarFeeds } from "../../../calendar/calendarFeeds.graphql";

export default {
  name: "Management",
  mixins: [managementMixin],
  data() {
    return {
      internalCalendars: "",
      calendarFeeds: [],
    };
  },
  mounted() {
    this.internalCalendars = this.widget.selectedCalendars;
  },
  apollo: {
    calendarFeeds: {
      query: calendarFeeds,
      update: (data) => data.calendar.calendarFeeds,
    },
  },
  methods: {
    updateStatus(calendars) {
      this.mutate(
        updateCalendarWidgets,
        {
          input: [
            {
              id: this.widget.id,
              selectedCalendars: calendars,
            },
          ],
        },
        (cached, incoming) => {
          incoming.forEach((widget) => {
            const index = cached.findIndex((c) => c.id === widget.id);
            cached[index].status = widget.status;
            cached[index].title = widget.title;
            cached[index].selectedCalendars = widget.selectedCalendars;
          });
          return cached;
        },
      );
    },
  },
};
</script>

<template>
  <v-card :elevation="0">
    <v-card-text class="pb-0">
      <message-box type="info">
        {{
          $t(
            "dashboard.dashboard_widgets.calendar.fields.selected_calendars_hint",
          )
        }}
      </message-box>
      <div class="grid">
        <v-checkbox
          v-model="internalCalendars"
          v-for="feed in calendarFeeds"
          :key="feed.name"
          :label="feed.verboseName"
          :value="feed.name"
          :color="feed.color"
        />
      </div>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <save-button
        :loading="loading"
        @click="updateStatus(internalCalendars)"
      />
    </v-card-actions>
  </v-card>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
}
</style>
