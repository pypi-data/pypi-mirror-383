<script setup>
import PersonalTodoForm from "../form/Personal_TodoForm.vue";

import DeleteButton from "../../generic/buttons/DeleteButton.vue";
import DeleteDialog from "../../generic/dialogs/DeleteDialog.vue";
import EditButton from "../../generic/buttons/EditButton.vue";

import BaseCalendarFeedListItem from "../../calendar/BaseCalendarFeedListItem.vue";
</script>

<template>
  <base-calendar-feed-list-item
    v-bind="$props"
    @refresh-calendar="$emit('refreshCalendar')"
  >
    <template v-if="meta?.can_edit || meta?.can_delete" #actions>
      <v-row>
        <!--
          Dialog with button to edit the personal todo.
        -->
        <personal-todo-form
          v-if="meta?.can_edit"
          :edit-item="initPatchData"
          @save="$emit('refreshCalendar')"
        >
          <template #activator="{ on, attrs }">
            <edit-button
              v-if="meta?.can_edit"
              v-bind="attrs"
              v-on="on"
              color="secondary"
              icon
            />
          </template>
        </personal-todo-form>

        <!--
          Dialog with button to delete the personal todo.
        -->
        <delete-button
          v-if="meta?.can_delete"
          @click="deleteDialog = true"
          color="error"
          icon
        />
        <delete-dialog
          v-if="meta?.can_delete"
          :items="[{ id: meta?.id, name: selectedEvent.name }]"
          :gql-delete-mutation="deleteMutation"
          v-model="deleteDialog"
          @save="updateOnSave()"
        />
      </v-row>
    </template>
  </base-calendar-feed-list-item>
</template>

<script>
import { DateTime } from "luxon";

import calendarFeedListItemMixin from "../../../mixins/calendarFeedListItem.js";

import { deletePersonalTodos } from "../../calendar/personal_todo/personalTodo.graphql";

export default {
  name: "PersonalTodoListItem",
  mixins: [calendarFeedListItemMixin],
  data() {
    return {
      deleteDialog: false,
      deleteMutation: deletePersonalTodos,
    };
  },
  emits: ["refreshCalendar"],
  methods: {
    updateOnSave() {
      this.$emit("refreshCalendar");
      this.deleteDialog = false;
    },
  },
  computed: {
    meta() {
      return JSON.parse(this.selectedEvent.meta);
    },
    initPatchData() {
      const start = this.$parseISODate(this.selectedEvent.start);
      let end = this.$parseISODate(this.selectedEvent.end);
      if (this.selectedEvent.allDay) {
        end = end.minus({ days: 1 });
      }
      return {
        id: this.meta?.id,
        persons: this.meta?.persons.map((p) => p.id.toString()),
        groups: this.meta?.groups.map((g) => g.id.toString()),
        title: this.selectedEvent.name,
        description: this.selectedEvent.description,
        location: this.selectedEvent.location,
        datetimeStart: start.toISO(),
        datetimeEnd: end.toISO(),
        dateStart: start.toISODate(),
        dateEnd: end.toISODate(),
        fullDay: this.selectedEvent.allDay,
        recurrences: this.meta?.recurrences,
        recurring: !!this.meta?.recurrences,
        completed: this.selectedEvent.completed
          ? this.selectedEvent.completed
          : DateTime.now(),
        percentComplete: this.selectedEvent.percentComplete,
      };
    },
  },
};
</script>
