<script setup>
import DateField from "./DateField.vue";
</script>

<template>
  <div>
    <v-row>
      <v-col class="py-0">
        <div>{{ $attrs.label }}</div>
      </v-col>
    </v-row>
    <v-row>
      <v-col v-if="!startDate" cols="4">
        <!--
          Field for start date
        -->
        <date-field
          v-model="start"
          v-bind="{ ...$attrs }"
          :label="$t('forms.recurrence.start')"
          :disabled="!frequency"
        />
      </v-col>
      <v-col :cols="startDate ? 8 : 4">
        <!--
          Field for recurrence frequency
        -->
        <v-select
          v-model="frequency"
          v-bind="{ ...$attrs }"
          :label="$t('forms.recurrence.frequency')"
          :items="rruleFrequencies"
          item-value="freq"
          :placeholder="$t('forms.recurrence.no_repeat')"
          clearable
        />
      </v-col>
      <v-col cols="4">
        <!--
          Field for end date
        -->
        <date-field
          v-model="until"
          v-bind="{ ...$attrs }"
          :label="$t('forms.recurrence.until')"
          :disabled="frequency === undefined"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { DateTime } from "luxon";
import { RRule } from "rrule";

export default {
  name: "RecurrenceField",
  data() {
    return {
      innerRecurrenceOptions: {},
      rruleFrequencies: [
        {
          freq: RRule.DAILY,
          text: this.$t("forms.recurrence.frequencies.daily"),
        },
        {
          freq: RRule.WEEKLY,
          text: this.$t("forms.recurrence.frequencies.weekly"),
        },
        {
          freq: RRule.MONTHLY,
          text: this.$t("forms.recurrence.frequencies.monthly"),
        },
        {
          freq: RRule.YEARLY,
          text: this.$t("forms.recurrence.frequencies.yearly"),
        },
      ],
    };
  },
  props: {
    value: {
      type: String,
      required: false,
      default: undefined,
    },
    startDate: {
      type: DateTime,
      required: false,
      default: undefined,
    },
  },
  computed: {
    frequency: {
      /**
       * Gets/sets the recurrence options.
       */

      get() {
        return this.innerRecurrenceOptions?.freq;
      },
      set(value) {
        this.innerRecurrenceOptions.freq = value;

        /**
         * Input event. Emits the recurrence options as a RRule string
         * when a value is set.
         */
        this.$emit("input", RRule.optionsToString(this.innerRecurrenceOptions));
      },
    },
    start: {
      /**
       * Gets/sets the end date.
       *
       * Converts to/from the JS date object format since the RRule library
       * can only handle such; and uses UTC time since the library recommends
       * doing so.
       */

      get() {
        return this.innerRecurrenceOptions?.dtstart
          ? DateTime.fromJSDate(this.innerRecurrenceOptions.dtstart).toISODate()
          : null;
      },
      set(value) {
        if (value) {
          const date = DateTime.fromISO(value).toUTC().toJSDate();
          this.innerRecurrenceOptions.dtstart = date;
        } else {
          delete this.innerRecurrenceOptions.dtstart;
        }

        /**
         * Input event. Emits the recurrence options as a RRule string
         * when a value is set.
         */
        this.$emit("input", RRule.optionsToString(this.innerRecurrenceOptions));
      },
    },
    until: {
      /**
       * Gets/sets the end date.
       *
       * Converts to/from the JS date object format since the RRule library
       * can only handle such; and uses UTC time since the library recommends
       * doing so.
       */

      get() {
        return this.innerRecurrenceOptions?.until
          ? DateTime.fromJSDate(this.innerRecurrenceOptions.until).toISODate()
          : null;
      },
      set(value) {
        if (value) {
          const date = DateTime.fromISO(value).toUTC().toJSDate();
          this.innerRecurrenceOptions.until = date;
        } else {
          delete this.innerRecurrenceOptions.until;
        }

        /**
         * Input event. Emits the recurrence options as a RRule string
         * when a value is set.
         */
        this.$emit("input", RRule.optionsToString(this.innerRecurrenceOptions));
      },
    },
  },
  watch: {
    value: {
      /**
       * Sets the inner RRule options value on value changes by
       * parsing the passed RRUle string.
       */

      immediate: true,
      handler(newValue) {
        this.innerRecurrenceOptions = newValue
          ? RRule.parseString(newValue)
          : {};
      },
    },
    startDate: {
      /**
       * Sets the start date of the inner RRule options
       * to the value of the startDate property.
       */

      deep: true,
      immediate: true,
      handler(newValue) {
        Object.assign(this.innerRecurrenceOptions, {
          dtstart: newValue.toUTC().startOf("day").toJSDate(),
        });
      },
    },
  },
};
</script>

<style scoped></style>
