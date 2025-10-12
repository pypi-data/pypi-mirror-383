/**
 * Mixin for use with calendar components.
 */

import { gqlCalendar } from "./calendar.graphql";
import { useDate } from "vuetify";
import { DateTime } from "luxon";
import { ref, computed, reactive, watch } from "vue";
import { useQuery } from "../../composables/app/apollo";

export function useEventColors() {
  function getColorForEvent(event) {
    if (event.status === "CANCELLED") {
      return event.color + "40";
    }
    return event.color;
  }

  function getTextColorForEvent(event) {
    if (event.status === "CANCELLED") {
      return event.color;
    }
    return "white";
  }

  return {
    getColorForEvent,
    getTextColorForEvent,
  };
}

export function useCalendar(calendarFeeds, params) {
  const dateToolKit = useDate();

  const calendar = reactive({
    calendarFeeds: [],
  });

  const selectedEvent = ref(null);
  const fetchedDateRanges = ref([]);
  const fetchMoreInterval = ref(null);

  const range = reactive({
    start: DateTime.now(),
    end: DateTime.now(),
  });

  const extendedStart = computed(() => dateToolKit.startOfWeek(range.start));
  const extendedEnd = computed(() => dateToolKit.endOfWeek(range.end));
  const queryVariables = computed(() => ({
    start: extendedStart.value.toISODate(),
    end: extendedEnd.value.toISODate(),
    names: calendarFeeds.value.map((f) => f.name),
    params: params.value !== null ? JSON.stringify(params.value) : null,
  }));

  const mergedFetchedDateRanges = computed(() => {
    let sortedRanges = fetchedDateRanges.value
      .slice()
      .sort((a, b) => a.start - b.start);

    let mergedRanges = [];

    for (const range of sortedRanges) {
      if (mergedRanges.length === 0) {
        mergedRanges.push(range);
      } else {
        let lastMergedRange = mergedRanges[mergedRanges.length - 1];
        let currentStartDate = range.start;
        let currentEndDate = range.end;
        let lastMergedEndDate = lastMergedRange.end.plus({ days: 1 });

        if (currentStartDate <= lastMergedEndDate) {
          lastMergedRange.end =
            currentEndDate > lastMergedEndDate
              ? currentEndDate
              : lastMergedRange.end;
        } else {
          mergedRanges.push(range);
        }
      }
    }

    return mergedRanges;
  });

  const { result, onResult, loading, error, refetch, fetchMore } = useQuery(
    gqlCalendar,
    queryVariables,
    { pollInterval: 30_000 },
  );

  onResult((result) => {
    if (!result?.data?.calendar) return;

    calendar.calendarFeeds = result.data.calendar.calendarFeeds;
  });

  watch(params, () => {
    if (range.start && range.end) {
      refetchWithNewParams();
    }
  });

  watch(calendarFeeds, (newFeeds, oldFeeds) => {
    if (
      !newFeeds
        .map((ncf) => ncf.name)
        .every((n) => oldFeeds.map((ocf) => ocf.name).includes(n))
    ) {
      refetchWithNewParams();
    }
  });

  watch(range, fetch, { deep: true, immediate: true });

  function isFullyContained(start, end) {
    for (const existingRange of mergedFetchedDateRanges.value) {
      if (start >= existingRange.start && end <= existingRange.end) {
        return true;
      }
    }

    return false;
  }

  function fetch() {
    refetch();

    if (calendar.calendarFeeds.length === 0) {
      // No calendar feeds have been fetched yet,
      // so fetch all events in the current date range

      fetchedDateRanges.value.push({
        start: extendedStart.value,
        end: extendedEnd.value,
      });
    } else if (!isFullyContained(extendedStart.value, extendedEnd.value)) {
      refresh();

      fetchedDateRanges.value.push({
        start: extendedStart.value,
        end: extendedEnd.value,
      });
    } else {
      clearInterval(fetchMoreInterval.value);

      fetchMoreInterval.value = setInterval(() => {
        fetchMoreCalendarEvents(extendedStart.value, extendedEnd.value);
      }, 30000);

      // Also reset the currently selected event (for the detail view)
      selectedEvent.value = null;
    }
  }

  function fetchMoreCalendarEvents(start, end) {
    fetchMore({
      variables: queryVariables.value,
      updateQuery: (previousResult, { fetchMoreResult }) => {
        let previousCalendarFeeds = previousResult.calendar.calendarFeeds;
        let newCalendarFeeds = fetchMoreResult.calendar.calendarFeeds;

        previousCalendarFeeds.forEach((calendarFeed, i, calendarFeeds) => {
          // Get all events except those that are updated
          let keepEvents = [];

          if (!start.invalid && !end.invalid) {
            keepEvents = calendarFeed.events.filter(
              (event) =>
                dateToolKit.isAfter(event.start, end) ||
                dateToolKit.isBefore(event.end, start),
            );
          } else if (!start.invalid) {
            keepEvents = calendarFeed.events.filter((event) =>
              dateToolKit.isBefore(event.end, start),
            );
          } else if (!end.invalid) {
            keepEvents = calendarFeed.events.filter((event) =>
              dateToolKit.isAfter(event.start, end),
            );
          }

          /// Update the events of the calendar feed
          calendarFeeds[i].events = [
            ...keepEvents,
            ...newCalendarFeeds[i].events,
          ];
        });
        return {
          calendar: {
            ...previousResult.calendar,
            calendarFeeds: previousCalendarFeeds,
          },
        };
      },
    });
  }

  function refresh() {
    clearInterval(fetchMoreInterval);

    fetchMoreCalendarEvents(extendedStart.value, extendedEnd.value);

    fetchMoreInterval.value = setInterval(() => {
      fetchMoreCalendarEvents(extendedStart.value, extendedEnd.value);
    }, 30_000);

    // Also reset the currently selected event (for the detail view)
    selectedEvent.value = null;
  }

  function refetchWithNewParams() {
    // Stop polling the query with old variables
    clearInterval(fetchMoreInterval.value);
    refetch();

    // Reset fetched date ranges to newly fetched date range
    fetchedDateRanges.value = [
      { start: extendedStart.value, end: extendedEnd.value },
    ];
  }

  return {
    loading,
    calendar,
    selectedEvent,
    range,
    ...useEventColors(),
    fetch,
    refresh,
    refetchWithNewParams,
  };
}
