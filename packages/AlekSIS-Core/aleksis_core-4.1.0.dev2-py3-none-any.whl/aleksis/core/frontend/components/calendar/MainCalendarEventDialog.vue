<script setup>
import CalendarEventDialog from "./CalendarEventDialog.vue";
import PersonField from "../generic/forms/PersonField.vue";
import GroupField from "../generic/forms/GroupField.vue";
import DateTimeField from "../generic/forms/DateTimeField.vue";
import PercentCompleteField from "./personal_todo/PercentCompleteField.vue";
</script>

<template>
  <calendar-event-dialog
    v-bind="$attrs"
    :events="events"
    :title-required="!isAvailabilityEvent"
    @selected-event="selectedEvent = $event"
  >
    <template #activator="{ props }">
      <slot name="activator" v-bind="{ props, events }" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #description.field="{ props }">
      <v-textarea rows="1" auto-grow v-bind="props" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #location.field="{ props }">
      <v-slide-y-reverse-transition appear>
        <v-text-field v-bind="props" />
      </v-slide-y-reverse-transition>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #persons.field="{ props }">
      <v-slide-y-reverse-transition appear>
        <person-field
          v-if="
            checkPermission('core.create_personal_event_with_invitations_rule')
          "
          multiple
          v-bind="props"
        />
      </v-slide-y-reverse-transition>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #groups.field="{ props }">
      <v-slide-y-reverse-transition appear>
        <group-field
          v-if="
            checkPermission('core.create_personal_event_with_invitations_rule')
          "
          multiple
          v-bind="props"
        />
      </v-slide-y-reverse-transition>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #percentComplete.field="{ props, item }">
      <v-slide-y-reverse-transition appear>
        <percent-complete-field v-bind="props" />
      </v-slide-y-reverse-transition>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #completed.field="{ props, item }">
      <v-slide-y-reverse-transition appear>
        <date-time-field
          v-show="item.percentComplete === 100"
          dense
          hide-details="auto"
          v-bind="props"
        />
      </v-slide-y-reverse-transition>
    </template>
  </calendar-event-dialog>
</template>

<script>
import { DateTime } from "luxon";

import { publicAvailabilityTypes } from "../availability_type/availabilityType.graphql";

import permissionsMixin from "../../mixins/permissions.js";

export default {
  name: "MainCalendarEventDialog",
  extends: "CalendarEventDialog",
  mixins: [permissionsMixin],
  data() {
    return {
      selectedEvent: undefined,
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
  methods: {
    personalTodoFilter(item) {
      if (item.percentComplete !== 100) {
        item.completed = null;
      }

      return item;
    },
  },
  computed: {
    isAvailabilityEvent() {
      return (
        typeof this.selectedEvent == "string" &&
        this.selectedEvent.startsWith("availability-type-")
      );
    },
    events() {
      let events = {
        personalEvent: {
          textKey: "calendar.create_event.event_types.personal_event",
          iconText: "mdi-calendar-account-outline",
          color: "primary",
          fields: {
            description: {
              default: undefined,
              cols: 12,
            },
            location: {
              default: undefined,
              cols: 12,
              textKey: "calendar.create_event.personal_events.location",
            },
            persons: {
              default: [],
              cols: 6,
              textKey: "calendar.create_event.personal_events.persons",
            },
            groups: {
              default: [],
              cols: 6,
              textKey: "calendar.create_event.personal_events.groups",
            },
          },
          objectSchemaType: "PersonalEventType",
        },
        personalTodo: {
          textKey: "calendar.create_event.event_types.personal_todo",
          iconText: "mdi-checkbox-marked-circle-plus-outline",
          color: "warning",
          fields: {
            datetimeEnd: {
              default: DateTime.now()
                .startOf("minute")
                .plus({ hours: 1 })
                .toISO({ suppressSeconds: true }),
              textKey: "calendar.create_event.personal_todos.due",
              cols: 6,
            },
            description: {
              default: undefined,
              cols: 12,
            },
            location: {
              default: undefined,
              cols: 12,
              textKey: "calendar.create_event.personal_todos.location",
            },
            persons: {
              default: [],
              cols: 6,
              textKey: "calendar.create_event.personal_todos.persons",
            },
            groups: {
              default: [],
              cols: 6,
              textKey: "calendar.create_event.personal_todos.groups",
            },
            percentComplete: {
              default: 0,
              cols: 12,
              textKey: "calendar.create_event.personal_todos.percent_completed",
            },
            completed: {
              default: DateTime.now(),
              cols: 12,
              textKey: "calendar.create_event.personal_todos.completed",
            },
          },
          filter: this.personalTodoFilter,
          objectSchemaType: "PersonalTodoType",
        },
      };

      this.availabilityTypes.forEach((type) => {
        events[`availability-type-${type.id}`] = {
          textKey:
            type.shortName === "f" || type.shortName === "b"
              ? `calendar.create_event.event_types.${type.shortName}`
              : type.name,
          iconText:
            {
              f: "mdi-calendar-check-outline",
              b: "mdi-calendar-remove-outline",
            }[type.shortName] || "mdi-calendar-clock",
          color:
            {
              f: "success",
              b: "error",
            }[type.shortName] || "secondary",
          fields: {
            description: {
              default: undefined,
              cols: 12,
            },
          },
          filter: (object) => ({ ...object, availabilityType: type.id }),
          objectSchemaType: "AvailabilityEventType",
        };
      });

      return events;
    },
  },
  mounted() {
    this.addPermissions(["core.create_personal_event_with_invitations_rule"]);
  },
};
</script>
