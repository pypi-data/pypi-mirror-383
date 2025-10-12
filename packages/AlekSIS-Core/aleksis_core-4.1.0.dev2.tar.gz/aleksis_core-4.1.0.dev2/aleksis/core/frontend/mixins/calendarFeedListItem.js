/**
 * Mixin for use with adaptable list items for calendar events.
 */
const calendarFeedListItemMixin = {
  props: {
    selectedEvent: {
      required: false,
      type: Object,
    },
  },
  computed: {
    completed() {
      return this.selectedEvent.percentComplete === 100;
    },
  },
};

export default calendarFeedListItemMixin;
