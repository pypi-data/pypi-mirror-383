/**
 * Mixin for use with adaptable components showing event bar for calendar feeds.
 */
const calendarFeedEventBarMixin = {
  props: {
    event: {
      required: true,
      type: Object,
    },
    eventParsed: {
      required: true,
      type: Object,
    },
    calendarType: {
      required: true,
      type: String,
    },
  },
};

export default calendarFeedEventBarMixin;
