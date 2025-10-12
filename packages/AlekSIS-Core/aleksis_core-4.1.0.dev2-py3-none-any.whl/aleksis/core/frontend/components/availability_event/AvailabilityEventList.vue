<script setup>
import { computed } from "vue";
import CRUDProvider from "../generic/crud/CRUDProvider.vue";
import { useCRUD } from "../../composables/crud/useCRUD.js";
import { publicAvailabilityTypes } from "../availability_type/availabilityType.graphql";

import { RRule } from "rrule";

import { useI18n } from "../../composables/app/useI18n";

const { t, d } = useI18n();

const availabilityTypes = useCRUD({ query: publicAvailabilityTypes });
const selectableEvents = computed(() =>
  availabilityTypes.items.map((type) => `availability-type-${type.id}`),
);

function getAvailabilityIcon(item) {
  return item.availabilityType.free
    ? "mdi-calendar-check-outline"
    : "mdi-calendar-remove-outline";
}
function getStartString(event) {
  if (event.datetimeStart) {
    return d(event.datetimeStart, "longNumeric");
  } else if (event.dateStart) {
    return d(event.dateStart);
  }
}
function getEndString(event) {
  if (event.datetimeEnd) {
    return d(event.datetimeEnd, "longNumeric");
  } else if (event.dateEnd) {
    return d(event.dateEnd);
  }
}

const rruleFrequencies = [
  {
    freq: RRule.DAILY,
    text: t("forms.recurrence.frequencies.daily"),
  },
  {
    freq: RRule.WEEKLY,
    text: t("forms.recurrence.frequencies.weekly"),
  },
  {
    freq: RRule.MONTHLY,
    text: t("forms.recurrence.frequencies.monthly"),
  },
  {
    freq: RRule.YEARLY,
    text: t("forms.recurrence.frequencies.yearly"),
  },
];

function rRuleToText(rfcString) {
  if (rfcString) {
    const rRule = RRule.fromString(rfcString);
    let recurrence = rruleFrequencies.find(
      (r) => r.freq === rRule.options.interval,
    ).text;
    if (rRule.options.until) {
      recurrence += `, ${t("availability_events.recurrences.until")} ${d(
        rRule.options.until,
        "short",
      )}`;
    }
    return recurrence;
  }
  return t("availability_events.recurrences.none");
}
</script>

<template>
  <!-- item-title-attribute="description" -->
  <c-r-u-d-provider
    :object-schema="{ type: 'AvailabilityEventType' }"
    disable-create
    disable-inline-edit
  >
    <!-- TODO: Port after CalendarEventDialog -->
    <!-- <template #additionalActions="{ attrs, on, editItem }"> -->
    <!--   <main-calendar-event-dialog -->
    <!--     v-bind="attrs" -->
    <!--     v-on="on" -->
    <!--     :initial-selected-event="`availability-type-${editItem.availabilityType.id}`" -->
    <!--     :selectable-events="selectableEvents" -->
    <!--   > -->
    <!--     <template #activator="{ attrs, on }"> -->
    <!--       <create-button v-bind="attrs" v-on="on" color="secondary" /> -->
    <!--     </template> -->
    <!--   </main-calendar-event-dialog> -->
    <!-- </template> -->

    <template #item.availabilityType="{ item }">
      <v-chip
        class="ma-2"
        :color="
          item.availabilityType.color
            ? item.availabilityType.color
            : item.availabilityType.free
              ? 'green'
              : 'red'
        "
        variant="outlined"
      >
        <v-icon start>
          {{ getAvailabilityIcon(item) }}
        </v-icon>
        {{
          item.availabilityType.shortName === "f" ||
          item.availabilityType.shortName === "b"
            ? t(
                `calendar.create_event.event_types.${item.availabilityType.shortName}`,
              )
            : item.availabilityType.name
        }}
      </v-chip>
    </template>

    <template #item.datetimeStart="{ item }">
      {{ getStartString(item) }}
    </template>

    <template #item.datetimeEnd="{ item }">
      {{ getEndString(item) }}
    </template>

    <template #item.recurrences="{ item }">
      {{ rRuleToText(item.recurrences) }}
    </template>

    <template #item.title="{ item }">
      {{ item.title ? item.title : "-" }}
    </template>

    <template #item.description="{ item }">
      {{ item.description ? item.description : "-" }}
    </template>
  </c-r-u-d-provider>
</template>
