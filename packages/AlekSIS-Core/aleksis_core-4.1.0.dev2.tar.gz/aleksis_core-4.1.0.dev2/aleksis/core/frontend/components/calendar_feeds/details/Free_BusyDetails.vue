<template>
  <base-calendar-feed-details v-bind="$props">
    <template #description="{ selectedEvent }">
      <v-divider
        inset
        v-if="selectedEvent.description && !withoutDescription"
      />

      <!--
            Description of the free/busy event
          -->
      <v-list-item v-if="selectedEvent.description && !withoutDescription">
        <template #prepend>
          <v-icon color="primary">mdi-card-text-outline</v-icon>
        </template>
        <div style="white-space: pre-line">
          {{ selectedEvent.description }}
        </div>
      </v-list-item>

      <!--
            Linked groups of the free/busy event
        -->
      <v-list-item v-if="selectedEvent.meta.groups.length">
        <template #prepend>
          <v-icon color="primary">mdi-account-group-outline</v-icon>
        </template>

        <v-list-item-title>
          <v-chip
            v-for="group in selectedEvent.meta.groups"
            :key="group.id"
            label
            variant="outlined"
            >{{ group.name }}</v-chip
          >
        </v-list-item-title>
      </v-list-item>

      <!--
            Linked persons of the free/busy event
        -->
      <v-list-item v-if="selectedEvent.meta.persons.length">
        <template #prepend>
          <v-icon color="primary">mdi-account-outline </v-icon>
        </template>

        <v-list-item-title>
          <v-chip
            v-for="person in selectedEvent.meta.persons"
            :key="person.id"
            label
            variant="outlined"
            >{{ person.full_name }}</v-chip
          >
        </v-list-item-title>
      </v-list-item>
    </template>
  </base-calendar-feed-details>
</template>

<script>
import calendarFeedDetailsMixin from "../../../mixins/calendarFeedDetails.js";
import BaseCalendarFeedDetails from "../../calendar/BaseCalendarFeedDetails.vue";

export default {
  name: "FreeBusyDetails",
  components: {
    BaseCalendarFeedDetails,
  },
  mixins: [calendarFeedDetailsMixin],
};
</script>
