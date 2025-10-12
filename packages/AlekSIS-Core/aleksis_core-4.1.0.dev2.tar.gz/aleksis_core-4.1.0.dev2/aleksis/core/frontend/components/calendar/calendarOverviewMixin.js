/**
 * Mixin for use with calendar components.
 */

import { DateTime } from "luxon";

const calendarOverviewMixin = {
  data() {
    return {
      calendarFocus: DateTime.now(),
      calendarType: "week",
      calendarView: "calendar",
    };
  },
  methods: {
    setCalendarFocus(val) {
      this.calendarFocus = val;
    },
    setCalendarType(val) {
      this.calendarType = val;
    },
  },
};

export default calendarOverviewMixin;
