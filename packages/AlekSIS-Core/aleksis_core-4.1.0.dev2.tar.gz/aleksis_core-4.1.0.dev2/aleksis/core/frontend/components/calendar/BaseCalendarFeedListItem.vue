<script setup>
import { DateTime } from "luxon";
</script>

<template>
  <ApolloMutation
    :mutation="setTodoCompletedMutation"
    :variables="{
      id: JSON.parse(selectedEvent.meta).id,
      completed: completed ? null : DateTime.now(),
    }"
    @done="$emit('refreshCalendar')"
  >
    <template #default="{ mutate, loading, error }">
      <v-list-item>
        <v-list-item-action>
          <v-checkbox
            v-if="!loading"
            :model-value="completed"
            @click="mutate"
          />
          <v-progress-circular indefinite v-else />
        </v-list-item-action>
        <v-list-item-title
          :class="{ 'text-decoration-line-through': completed }"
          >{{ selectedEvent.name }}</v-list-item-title
        >

        <v-list-item-subtitle>
          <v-chip
            v-if="selectedEvent.due"
            :color="
              $parseISODate(selectedEvent.due) < DateTime.now() ? 'error' : ''
            "
            size="small"
            variant="outlined"
          >
            <v-icon size="small" class="mr-1">{{
              getDueIcon(selectedEvent)
            }}</v-icon>
            {{ $d($parseISODate(selectedEvent.due), "shortDateTime") }}
          </v-chip>
          <v-chip
            v-if="selectedEvent.completed"
            color="success"
            size="small"
            variant="outlined"
            class="ml-2"
          >
            <v-icon size="small" class="mr-1">$success</v-icon>
            {{ $d($parseISODate(selectedEvent.completed), "shortDateTime") }}
          </v-chip>
        </v-list-item-subtitle>

        <v-list-item-subtitle v-if="selectedEvent.description">
          {{ selectedEvent.description }}
        </v-list-item-subtitle>

        <v-avatar v-if="selectedEvent.percentComplete">
          <v-progress-circular
            :model-value="selectedEvent.percentComplete"
            :size="40"
            :color="completed ? 'success' : 'primary'"
          >
            <div class="text-overline">
              <v-icon
                :color="completed ? 'success' : 'primary'"
                v-if="completed"
                >$success</v-icon
              >
              <template v-else>
                {{ `${selectedEvent.percentComplete}%` }}
              </template>
            </div>
          </v-progress-circular>
        </v-avatar>

        <v-list-item-action>
          <slot name="actions" :selected-event="selectedEvent" />
        </v-list-item-action>
      </v-list-item>
    </template>
  </ApolloMutation>
</template>

<script>
import { setTodoCompleted } from "./todos/todo.graphql";

import calendarFeedListItemMixin from "../../mixins/calendarFeedListItem.js";

export default {
  name: "BaseCalendarFeedListItem",
  mixins: [calendarFeedListItemMixin],
  data() {
    return {
      setTodoCompletedMutation: setTodoCompleted,
    };
  },
  methods: {
    getDueIcon(event) {
      return this.$parseISODate(event.due) < DateTime.now()
        ? "mdi-calendar-alert-outline"
        : "mdi-calendar-today-outline";
    },
  },
  emits: ["refreshCalendar"],
};
</script>
