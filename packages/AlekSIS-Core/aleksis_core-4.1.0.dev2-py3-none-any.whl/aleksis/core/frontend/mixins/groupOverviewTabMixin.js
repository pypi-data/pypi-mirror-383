/**
 * This mixin provides shared props for each group overview tab.
 */
export default {
  props: {
    /**
     * The group for the current group overview
     */
    group: {
      type: Object,
      required: true,
    },
    /**
     * The optional school term for the current group overview
     */
    schoolTerm: {
      type: Object,
      required: false,
      default: null,
    },
  },
};
