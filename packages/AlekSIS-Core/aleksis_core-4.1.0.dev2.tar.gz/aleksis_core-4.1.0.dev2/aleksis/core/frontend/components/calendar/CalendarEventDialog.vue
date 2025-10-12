<script setup>
import DateTimeField from "../generic/forms/DateTimeField.vue";
import DialogObjectForm from "../generic/dialogs/DialogObjectForm.vue";
import RecurrenceField from "../generic/forms/RecurrenceField.vue";
import CollapseTriggerButton from "../generic/buttons/CollapseTriggerButton.vue";
</script>

<template>
  <dialog-object-form
    v-bind="{ ...$props, ...$attrs }"
    :get-create-data="filterData"
    :get-patch-data="filterData"
    :default-item="defaultItem"
    :edit-item="editItemWithDatetimes"
    :fields="editableFields"
    :minimal-patch="false"
    :object-schema="selectedEventObjectSchema"
    @save="$emit('save', $event)"
  >
    <template #activator="{ props }">
      <slot name="activator" v-bind="{ props }" />
    </template>

    <template #title>
      <v-container class="d-flex flex-wrap">
        <v-icon class="mr-2">{{ titleIcon }}</v-icon>
        <v-chip-group v-model="selectedEvent" mandatory color="primary">
          <v-chip
            v-for="event in selectableEventsWithDefault"
            :key="event"
            :value="event"
          >
            <v-icon
              v-if="events[event].iconText"
              :color="events[event].color"
              size="small"
              start
            >
              {{ events[event].iconText }}
            </v-icon>
            {{ $t(events[event].textKey) }}
          </v-chip>
        </v-chip-group>
      </v-container>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #datetimeStart.field="{ props, item }">
      <div aria-required="true">
        <date-time-field
          dense
          hide-details="auto"
          v-bind="props"
          required
          :hide-time="item.fullDay"
        />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #datetimeEnd.field="{ props, item }">
      <div aria-required="true">
        <date-time-field
          dense
          hide-details="auto"
          v-bind="props"
          required
          :hide-time="item.fullDay"
        />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #fullDay.field="{ props }">
      <v-switch
        class="pt-0"
        density="compact"
        hide-details
        :true-value="true"
        :false-value="false"
        v-bind="props"
      />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #recurring.field="{ props, item }">
      <collapse-trigger-button
        class="mt-2 full-width"
        v-bind="props"
        :label-active="$t('calendar.create_event.is_recurring')"
      />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #recurrences.field="{ props, item }">
      <v-expand-transition>
        <recurrence-field
          v-show="item.recurring"
          v-bind="props"
          :start-date="DateTime.now()"
        />
      </v-expand-transition>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #title.field="{ props }">
      <div :aria-required="titleRequired">
        <v-text-field v-bind="props" required />
      </div>
    </template>

    <template v-for="(_, slot) of $slots" #[slot]="scope">
      <slot :name="slot" v-bind="scope" />
    </template>
  </dialog-object-form>
</template>

<script>
import { DateTime } from "luxon";

export default {
  name: "CalendarEventDialog",
  emits: ["selectedEvent", "save"],
  data() {
    return {
      baseEvent: {
        id: {
          default: undefined,
          hide: true,
        },
        datetimeStart: {
          default: DateTime.now()
            .startOf("minute")
            .toISO({ suppressSeconds: true }),
          cols: 6,
        },
        datetimeEnd: {
          default: DateTime.now()
            .startOf("minute")
            .plus({ hours: 1 })
            .toISO({ suppressSeconds: true }),
          cols: 6,
        },
        fullDay: {
          default: false,
          cols: 5,
          filter: true,
        },
        recurring: {
          cols: 7,
          textKey: "calendar.create_event.is_not_recurring",
          filter: true,
        },
        recurrences: {
          default: "",
          cols: 12,
        },
        title: {
          default: "",
          cols: 12,
        },
      },
      selectedEvent: this.initialSelectedEvent,
    };
  },
  props: {
    /**
     * An object with event-name and event-description key-value-pairs.
     *
     * @example {
     *            example-event-name:
     *              {
     *                // Required
     *                createMutation: exampleEventCreateMutation,
     *                updateMutation: exampleEventUpdateMutation,
     *                fields: {
     *                  example-field-name: {
     *                    // required
     *                    default: default-value,
     *                    cols: 6, // number of columns in dialog
     *                    // optional
     *                    textKey: "example-key", // key for field-name lookup
     *                    hide: true, // Hide this field in dialog
     *                    filter: false, // Filter this result from object send to server
     *                  },
     *                  ...
     *                },
     *                // Optional
     *                textKey: "example-key", // key for event-name lookup
     *                filter: (object) => { Do something with object before sending to server }
     *                iconText: "mdi-calendar-account-outline", // Icon for event
     *                color: "primary", // Color for event
     *              },
     *            ...
     *          }
     */
    events: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    initialSelectedEvent: {
      type: String,
      required: false,
    },
    selectableEvents: {
      type: Array,
      required: false,
    },
    editItem: {
      type: Object,
      required: false,
      default: undefined,
    },
    value: {
      type: Boolean,
      required: false,
      default: undefined,
    },
    /**
     * Should title field be required?
     */
    titleRequired: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  methods: {
    camelToSnakeCase(str) {
      return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
    },
    formatField([name, { cols, textKey }]) {
      textKey =
        textKey || "calendar.create_event." + this.camelToSnakeCase(name);
      return {
        value: name,
        text: this.$t(textKey),
        cols: cols,
      };
    },
    filterData(item) {
      const fullDay = item.fullDay;
      const recurring = item.recurring;

      // Filter item to contain only fields without the filter prop,
      // suitable to the selected event and only those with defined
      // values
      item = Object.keys(this.fields)
        .filter((key) => !this.fields[key].filter)
        .map((name) => [name, item[name]])
        .filter(([name, value]) => value !== undefined);
      item = Object.fromEntries(item);

      if (fullDay) {
        item.dateStart = this.$parseISODate(item.datetimeStart).toISODate();
        item.dateEnd = this.$parseISODate(item.datetimeEnd).toISODate();
        delete item.datetimeStart;
        delete item.datetimeEnd;
      }

      if (!recurring) {
        delete item.timezone;
        delete item.recurrences;
      } else {
        item.timezone = DateTime.local().zoneName;
      }

      const filter = this.events[this.selectedEvent]?.filter;

      if (filter) {
        return filter(item);
      } else {
        return item;
      }
    },
  },
  computed: {
    // Needed since a prop's default can not access data
    selectableEventsWithDefault() {
      return this.selectableEvents
        ? this.selectableEvents
        : Object.keys(this.events);
    },
    // Contains all possible fields to facilitate event-switching while editing
    defaultItem() {
      const base = Object.entries(this.baseEvent).map(([event, val]) => [
        event,
        val.default,
      ]);
      const events = Object.entries(this.events).flatMap(([_, { fields }]) =>
        Object.entries(fields).map(([name, value]) => [name, value.default]),
      );
      return {
        ...Object.fromEntries(base),
        ...Object.fromEntries(events),
      };
    },
    selectedEventObjectSchema() {
      return { type: this.events[this.selectedEvent]?.objectSchemaType };
    },
    // All fields of the currently selected Event
    fields() {
      return {
        ...this.baseEvent,
        ...(this.events[this.selectedEvent]?.fields || {}),
      };
    },
    // Array of field definitions for DialogObjectForm
    editableFields() {
      return Object.entries(this.fields)
        .filter(([_, { hide }]) => !hide)
        .map(this.formatField);
    },
    // Assure editItem has datetime and recurring values set
    editItemWithDatetimes() {
      if (this.editItem) {
        let extraProps = {};
        if (
          this.editItem.datetimeStart === null &&
          this.editItem.datetimeEnd === null
        ) {
          extraProps = {
            datetimeStart: this.$parseISODate(
              this.editItem.dateStart,
            ).toISODate(),
            datetimeEnd: this.$parseISODate(this.editItem.dateEnd).toISODate(),
            fullDay: true,
          };
        }
        if (this.editItem.recurrences) {
          extraProps = {
            ...extraProps,
            recurring: true,
          };
        }
        return {
          ...this.editItem,
          ...extraProps,
        };
      } else {
        return undefined;
      }
    },
    titleIcon() {
      if (this.editItem) {
        return "$edit";
      }
      return "$plus";
    },
  },
  watch: {
    initialSelectedEvent: {
      handler(newVal) {
        this.selectedEvent = newVal;
      },
      immediate: true,
    },
    selectedEvent: {
      handler(newVal) {
        this.$emit("selectedEvent", newVal);
      },
      immediate: true,
    },
  },
};
</script>
