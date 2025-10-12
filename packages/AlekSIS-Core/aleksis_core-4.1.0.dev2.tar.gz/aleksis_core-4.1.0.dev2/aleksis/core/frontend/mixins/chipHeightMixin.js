const HEIGHTS = {
  "x-small": 16,
  small: 24,
  default: 32,
  large: 54,
  "x-large": 66,
};

/**
 * Mixin for vue components with the same heights as a v-chip
 */
export default {
  props: {
    size: {
      type: String,
      required: false,
      default: "default",
    },
  },
  computed: {
    computedHeight() {
      return Object.hasOwn(HEIGHTS, this.size)
        ? HEIGHTS[this.size]
        : HEIGHTS.default;
    },
    heightString() {
      return `${this.computedHeight}px`;
    },
    progressPadding() {
      return `${this.computedHeight / 2}px`;
    },
  },
};
