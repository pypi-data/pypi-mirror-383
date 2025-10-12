<template>
  <base-calendar-feed-details v-bind="$props">
    <template #description="{ selectedEvent }">
      <v-divider
        inset
        v-if="selectedEvent.description && !withoutDescription"
      />

      <!--
          Description of the availability event
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
          Type of the availability event
        -->
      <template v-if="selectedEvent.meta.availability_type">
        <v-divider />
        <v-list-item>
          <template #prepend>
            <v-icon color="primary">mdi-shape-outline</v-icon>
          </template>
          <div style="white-space: pre-line">
            {{
              `${selectedEvent.meta.availability_type.name} (${selectedEvent.meta.availability_type.short_name})`
            }}
          </div>
        </v-list-item>
      </template>
    </template>

    <!--
        Actions that can be performed on the availability event.
        Only shown when the respective permissions are present.
      -->
    <template
      v-if="selectedEvent.meta.can_edit || selectedEvent.meta.can_delete"
      #actions
    >
      <v-divider inset />
      <v-card-actions>
        <!--
            Dialog with button to edit the availability event.
          -->
        <main-calendar-event-dialog
          v-if="selectedEvent.meta.can_edit"
          :edit-item="initPatchData"
          :initial-selected-event="`availability-type-${initPatchData.availabilityType}`"
          :selectable-events="selectableEvents"
          @save="updateOnSave()"
        >
          <template #activator="{ on, attrs }">
            <edit-button
              v-if="selectedEvent.meta.can_edit"
              v-bind="attrs"
              v-on="on"
              color="secondary"
              outlined
            />
          </template>
        </main-calendar-event-dialog>

        <!--
            Dialog with button to delete the availability event.
          -->
        <delete-button
          v-if="selectedEvent.meta.can_delete"
          @click="deleteDialog = true"
          class="ml-2"
          color="error"
          text
        />
        <delete-dialog
          v-if="selectedEvent.meta.can_delete"
          :items="[{ id: selectedEvent.meta.id, name: selectedEvent.name }]"
          :gql-delete-mutation="deleteMutation"
          v-model="deleteDialog"
          @save="updateOnSave()"
        />
      </v-card-actions>
    </template>
  </base-calendar-feed-details>
</template>

<script>
import calendarFeedDetailsMixin from "../../../mixins/calendarFeedDetails.js";
import BaseCalendarFeedDetails from "../../calendar/BaseCalendarFeedDetails.vue";

import MainCalendarEventDialog from "../../calendar/MainCalendarEventDialog.vue";
import { deleteAvailabilityEvents } from "../../availability_event/availabilityEvent.graphql";

import DeleteButton from "../../generic/buttons/DeleteButton.vue";
import DeleteDialog from "../../generic/dialogs/DeleteDialog.vue";
import EditButton from "../../generic/buttons/EditButton.vue";

import { publicAvailabilityTypes } from "../../availability_type/availabilityType.graphql";

export default {
  name: "AvailabilitiesDetails",
  components: {
    BaseCalendarFeedDetails,
    MainCalendarEventDialog,
    DeleteButton,
    DeleteDialog,
    EditButton,
  },
  mixins: [calendarFeedDetailsMixin],
  data() {
    return {
      deleteDialog: false,
      deleteMutation: deleteAvailabilityEvents,
      availabilityTypes: [],
    };
  },
  apollo: {
    availabilityTypes: {
      query: publicAvailabilityTypes,
      update(data) {
        return data.items;
      },
    },
  },
  emits: ["refreshCalendar"],
  methods: {
    updateOnSave() {
      this.$emit("refreshCalendar");
      this.model = false;
    },
  },
  computed: {
    initPatchData() {
      return {
        id: this.selectedEvent.meta.id,
        title: this.selectedEvent.meta.title,
        description: this.selectedEvent.meta.description,
        availabilityType: this.selectedEvent.meta.availability_type.id,
        datetimeStart: this.selectedEvent.startDateTime.toISO(),
        datetimeEnd: this.selectedEvent.endDateTime.toISO(),
        dateStart: this.selectedEvent.startDateTime.toISODate(),
        dateEnd: this.selectedEvent.endDateTime.toISODate(),
        fullDay: this.selectedEvent.allDay,
        recurrences: this.selectedEvent.meta.recurrences,
        recurring: !!this.selectedEvent.meta.recurrences,
      };
    },
    selectableEvents() {
      return this.availabilityTypes.map(
        (type) => `availability-type-${type.id}`,
      );
    },
  },
};
</script>
