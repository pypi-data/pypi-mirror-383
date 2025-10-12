<template>
  <div>
    <!-- Calendar title with current calendar time range -->
    <v-sheet :height="height">
      <v-expand-transition>
        <v-progress-linear v-if="loading" indeterminate />
      </v-expand-transition>
      <v-calendar
        ref="cal"
        v-model="focus"
        show-week
        :events="events"
        :weekdays="daysOfWeek"
        :view-mode="type"
        :event-color="getColorForEvent"
        :event-text-color="getTextColorForEvent"
        :first-time="startWithFirstTime ? firstTime : undefined"
        :interval-height="60"
        @click:date="viewDay"
        @click:day="viewDay"
        @click:more="viewDay"
        @click:event="viewEvent"
      >
        <template #day-body="{ date, week }">
          <div
            v-show="!!week"
            class="v-current-time"
            :class="{ first: date === week?.[0]?.date }"
            :style="{ top: nowY }"
          ></div>
        </template>
        <!--          <div-->
        <template #interval-event="{ height, margin, event, interval }">
          <VSheet
            @click="viewEvent($event, event)"
            :height="height"
            density="comfortable"
            :style="{ marginTop: margin }"
            class="v-calendar-internal-event"
            :color="event?.color ?? undefined"
            :rounded="
              event?.first && event?.last
                ? true
                : event?.first
                  ? 't'
                  : event?.last
                    ? 'b'
                    : false
            "
          >
            <component
              :is="eventBarComponentForFeed(event.calendarFeedName)"
              :event="event"
              :event-parsed="event"
              :calendar-type="type"
            />
          </VSheet>
        </template>
        <template
          v-if="Object.keys(daysWithHiddenEvents).length"
          #interval-header
        >
          <div
            v-if="
              !type === 'day' ||
              Object.keys(daysWithHiddenEvents).includes(focus)
            "
            class="d-flex justify-center align-end"
            :style="{ height: '100%' }"
          >
            <v-btn
              icon
              class="ma-2"
              @click="showAllAllDayEvents = !showAllAllDayEvents"
            >
              <v-icon>{{ showAllAllDayEventsButtonIcon }}</v-icon>
            </v-btn>
          </div>
        </template>
        <template #day-header="{ date }">
          <template
            v-if="
              Object.keys(daysWithHiddenEvents).includes(date) &&
              !showAllAllDayEvents
            "
          >
            <v-spacer />
            <div
              class="v-event-more ml-1"
              v-ripple
              @click="showAllAllDayEvents = true"
            >
              {{ $t("calendar.more_events", daysWithHiddenEvents[date]) }}
            </div>
          </template>
        </template>
      </v-calendar>
      <component
        v-if="selectedEvent"
        :is="detailComponentForFeed(selectedEvent.calendarFeedName)"
        v-model="selectedOpen"
        :selected-element="selectedElement"
        :selected-event="selectedEvent"
        :calendar-type="type"
        @refresh-calendar="refresh()"
      />
    </v-sheet>
  </div>
</template>

<script setup>
import GenericCalendarFeedDetails from "./GenericCalendarFeedDetails.vue";
import GenericCalendarFeedEventBar from "./GenericCalendarFeedEventBar.vue";

import {
  calendarFeedDetailComponents,
  calendarFeedEventBarComponents,
} from "aleksisAppImporter";

import { useCalendar } from "./calendarMixin.js";
import { useInterval } from "../../composables/utils/useInterval";

import { Interval, DateTime } from "luxon";

import {
  defineModel,
  defineProps,
  ref,
  reactive,
  computed,
  watch,
  watchEffect,
  onMounted,
  toRef,
  toRefs,
} from "vue";

// Array of length one (one datetime)
const focus = defineModel("focus", { type: Array, default: [DateTime.now()] });
const type = defineModel("type", { type: String });

watch(type, (newType) => {
  if (!["day", "week", "month"].includes(newType)) {
    type.value = "week";
  }
});

const props = defineProps({
  // Start the calendar with the time of the first starting calendar event
  startWithFirstTime: {
    type: Boolean,
    required: false,
    default: () => false,
  },
  height: {
    type: String,
    required: false,
    default: "600",
  },
  calendarDaysOfWeek: {
    type: Array,
    required: false,
    default: undefined,
  },
  /**
   * What event/time to jump to.
   * Currently possible: `current` for current time, `first` for time of first visible event.
   * @values current, first
   */
  scrollTarget: {
    type: String,
    required: false,
    default: "current",
  },
  maxAllDayEvents: {
    type: Number,
    required: false,
    default: 5,
  },
  calendarFeeds: {
    type: Array,
    required: false,
    default: () => [],
  },
  params: {
    type: Object,
    required: false,
    default: null,
  },
});

const selectedElement = ref(null);
const selectedOpen = ref(false);

const firstTime = ref(1);
const scrolled = ref(false);

const personByIdOrMe = reactive({
  id: null,
  preferences: {
    daysOfWeek: [1, 2, 3, 4, 5, 6, 0],
  },
});

const {
  loading,
  calendar,
  selectedEvent,
  range,
  getColorForEvent,
  getTextColorForEvent,
  fetch,
  refresh,
  refetchWithNewParams,
} = toRefs(useCalendar(toRef(props, "calendarFeeds"), toRef(props, "params")));

const showAllAllDayEvents = ref(false);
const daysWithHiddenEvents = ref({});

const ready = ref(false);

// TODO
// apollo: {
//   personByIdOrMe: {
//     query: calendarDaysPreference,
//     skip() {
//       return this.calendarDaysOfWeek !== undefined;
//     },
//   },
// }

const events = computed(() => {
  let events = calendar.value.calendarFeeds
    .filter((c) => props.calendarFeeds.map((cf) => cf.name).includes(c.name))
    .flatMap((cf) =>
      cf.events.map((event) => {
        const start = DateTime.fromISO(event.start);
        let end = DateTime.fromISO(event.end);
        if (event.allDay) {
          end = end.minus({ days: 1 });
        }
        return {
          ...event,
          category: cf.verboseName,
          calendarFeedName: cf.name,
          start: start,
          end: end,
          startDateTime: start,
          endDateTime: end,
          color: event.color ? event.color : cf.color,
          timed: !event.allDay,
          meta: JSON.parse(event.meta),
        };
      }),
    );

  if (type.value === "month" || props.showAllAllDayEvents) {
    return events;
  }

  let dateFullEventCount = {};
  clearDaysWithHiddenEvents();

  return events.filter((event) => {
    if (!event.allDay) {
      return true;
    }
    const start = event.startDateTime;
    dateFullEventCount[start] = (dateFullEventCount[start] || 0) + 1;
    const show = dateFullEventCount[start] <= props.maxAllDayEvents;
    if (!show) {
      const dateInterval = Interval.fromDateTimes(
        start,
        event.endDateTime.endOf("day"),
      )
        .splitBy({ day: 1 })
        .map((date) => date.start.toISODate());
      for (const date of dateInterval) {
        daysWithHiddenEvents.value[date] =
          (daysWithHiddenEvents.value[date] || 0) + 1;
      }
    }
    return show;
  });
});

// TODO ???
const cal = ref();

// TODO
// const nowY = computed(() => cal.value ? cal.value.timeToY(cal.value.times.now) + "px" : "-10px");
const daysOfWeek = computed(() => {
  if (props.calendarDaysOfWeek !== undefined) {
    return props.calendarDaysOfWeek;
  }

  return personByIdOrMe.preferences.daysOfWeek;
});
const showAllAllDayEventsButtonIcon = computed(() =>
  showAllAllDayEvents.value ? "mdi-chevron-up" : "mdi-chevron-down",
);

const emit = defineEmits([
  "changeCalendarType",
  "changeCalendarFocus",
  "selectEvent",
]);

watch(selectedEvent, (val) => emit("selectEvent", val));

watch(range, updateMinTime, { deep: true });
watch(events, updateMinTime, { deep: true });
watch(props.calendarFeeds, (newFeeds, oldFeeds) => {
  updateMinTime();

  if (
    !newFeeds
      .map((ncf) => ncf.name)
      .every((n) => oldFeeds.map((ocf) => ocf.name).includes(n))
  ) {
    refetchWithNewParams();
  }
});

function viewDay({ date }) {
  focus.value = [date];
  type.value = "day";
}

function viewEvent(nativeEvent, event) {
  const open = () => {
    selectedEvent.value = event;
    selectedElement.value = nativeEvent.target;
    requestAnimationFrame(() =>
      requestAnimationFrame(() => (selectedOpen.value = true)),
    );
  };

  if (selectedOpen.value) {
    selectedOpen.value = false;
    requestAnimationFrame(() => requestAnimationFrame(() => open()));
  } else {
    open();
  }

  nativeEvent.stopPropagation();
}

function detailComponentForFeed(feedName) {
  if (
    calendar.value.calendarFeeds &&
    feedName &&
    Object.keys(calendarFeedDetailComponents).includes(feedName + "details")
  ) {
    return calendarFeedDetailComponents[feedName + "details"];
  }
  return GenericCalendarFeedDetails;
}

function eventBarComponentForFeed(feedName) {
  if (
    calendar.value.calendarFeeds &&
    feedName &&
    Object.keys(calendarFeedEventBarComponents).includes(feedName + "eventbar")
  ) {
    return calendarFeedEventBarComponents[feedName + "eventbar"];
  }
  return GenericCalendarFeedEventBar;
}

function updateMinTime() {
  // Set the minimum time of the calendar
  const visibileEvents = events.value.filter((event) => {
    return (
      (event.endDateTime ?? event.end).startOf("day") >=
        range.value.start.startOf("day") &&
      (event.startDateTime ?? event.start).startOf("day") <=
        range.value.end.startOf("day")
    );
  });
  const minuteTimes = visibileEvents.map((event) =>
    getMinutesAfterMidnight(event.startDateTime ?? event.start),
  );

  let minTime = minuteTimes.length > 0 ? Math.min.apply(Math, minuteTimes) : 0;

  // instead of first time take the previous full hour
  minTime = Math.floor(Math.max(0, minTime - 1) / 60) * 60;

  firstTime.value = minTime;

  // When events are loaded, scroll once
  if (!scrolled.value && minuteTimes.length > 0) {
    // TODO
    // scrollToTime();
  }
}

function getMinutesAfterMidnight(date) {
  return 60 * date.hour + date.minute;
}

watchEffect(() => {
  range.value.start = focus.value[0]
    .startOf(type.value ?? "week")
    .startOf("day");
  range.value.end = focus.value[0].endOf(type.value ?? "week").endOf("day");
});

// function getCurrentTime() {
//   return cal.value
//     ? cal.value.times.now.hour * 60 + cal.value.times.now.minute
//     : 0;
// }
//
// function scrollToTime() {
//       let first;
//
//       switch (props.scrollTarget.value) {
//         case "first": {
//           first = firstTime.value;
//           break;
//         }
//         case "current":
//         default: {
//           const time = getCurrentTime();
//           first = Math.max(0, time - (time % 30) - 30);
//           break;
//         }
//       }
//
//       if (props.startWithFirstTime) {
//         first = first - firstTime.value;
//       }
//
//       cal.value.scrollToTime(first);
//
//       scrolled.value = true;
// }

function updateTime() {
  useInterval(() => cal.value.updateTimes(), 60 * 1000);
}

function clearDaysWithHiddenEvents() {
  daysWithHiddenEvents.value = {};
}

onMounted(() => {
  ready.value = true;
  // this.$refs.cal.move(0);
  updateTime();
});
</script>

<style lang="scss">
.v-current-time {
  height: 2px;
  background-color: #ea4335;
  position: absolute;
  left: -1px;
  right: 0;
  pointer-events: none;

  &.first::before {
    content: "";
    position: absolute;
    background-color: #ea4335;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-top: -5px;
    margin-left: -6.5px;
  }
}
</style>
