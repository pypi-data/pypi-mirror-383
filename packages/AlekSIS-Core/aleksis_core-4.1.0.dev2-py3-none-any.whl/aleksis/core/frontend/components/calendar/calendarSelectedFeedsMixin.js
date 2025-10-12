/**
 * Mixin for use with adaptable components showing details for calendar feeds.
 */
import gqlCalendarFeeds from "./calendarFeeds.graphql";
import gqlSetCalendarStatus from "./setCalendarStatus.graphql";

const calendarSelectedFeedsMixin = {
  data() {
    return {
      calendar: {
        calendarFeeds: [],
      },
      selectedCalendarFeedNames: [],
    };
  },
  apollo: {
    calendar: {
      query: gqlCalendarFeeds,
      result({ data }) {
        if (data) {
          this.selectedCalendarFeedNames = data.calendar.calendarFeeds
            .filter((c) => c.activated)
            .map((c) => c.name);
        }
      },
    },
  },
  computed: {
    selectedFeedsForCalendar() {
      return this.selectedCalendarFeedNames.map((name) => {
        return { name };
      });
    },
    todoFeeds() {
      return this.calendar.calendarFeeds
        .filter((f) => f.componentType === "todo")
        .map((c) => ({ name: c.name }));
    },
  },
  methods: {
    storeActivatedCalendars() {
      // Store currently activated calendars in the backend
      this.$apollo.mutate({
        mutation: gqlSetCalendarStatus,
        variables: {
          calendars: this.selectedCalendarFeedNames,
        },
      });
    },
  },
};

export default calendarSelectedFeedsMixin;
