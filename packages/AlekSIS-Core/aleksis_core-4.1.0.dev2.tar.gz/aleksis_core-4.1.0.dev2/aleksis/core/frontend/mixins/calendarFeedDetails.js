/**
 * Mixin for use with adaptable components showing details for calendar feeds.
 */
const calendarFeedDetailsMixin = {
  props: {
    selectedElement: {
      required: false,
      default: null,
    },
    selectedEvent: {
      required: false,
      type: Object,
    },
    value: { type: Boolean, required: true },
    withoutTime: {
      required: false,
      type: Boolean,
      default: false,
    },
    withoutDescription: {
      required: false,
      type: Boolean,
      default: false,
    },
    withoutBadge: {
      required: false,
      type: Boolean,
      default: false,
    },
    withoutLocation: {
      required: false,
      type: Boolean,
      default: false,
    },
    color: {
      required: false,
      type: String,
      default: null,
    },
    calendarType: {
      required: true,
      type: String,
    },
  },
  computed: {
    model: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
};

export default calendarFeedDetailsMixin;
