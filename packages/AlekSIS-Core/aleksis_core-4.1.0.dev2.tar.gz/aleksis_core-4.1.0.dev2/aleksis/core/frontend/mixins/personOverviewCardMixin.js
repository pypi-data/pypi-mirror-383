/**
 * This mixin provides shared props for each person overview card.
 */
export default {
  props: {
    /**
     * The person for the current person overview
     */
    person: {
      type: Object,
      required: true,
    },
    /**
     * The optional school term for the current person overview
     */
    schoolTerm: {
      type: Object,
      required: false,
      default: null,
    },
    /**
     * Whether the current widget is maximized
     */
    maximized: {
      type: Boolean,
      required: false,
      default: false,
    },
    emits: [
      // When this is fired, the component can assume that the `maximized` prop will soon turn true
      "maximize",
      // Use this to signify a wanted closure
      "minimize",
    ],
  },
};
