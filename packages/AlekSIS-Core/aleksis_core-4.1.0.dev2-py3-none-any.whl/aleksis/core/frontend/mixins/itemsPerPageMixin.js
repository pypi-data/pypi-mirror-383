/**
 * This mixin provides generic options for pagination.
 */
export default {
  props: {
    /**
     * Number of items shown per page
     * @values natural number
     */
    itemsPerPage: {
      type: Number,
      required: false,
      default: 50,
    },
  },
  computed: {
    footerProps() {
      return {
        ...(this.$attrs["footer-props"] || {}),
        itemsPerPageOptions: [
          this.itemsPerPage,
          this.itemsPerPage * 2,
          this.itemsPerPage * 4,
          -1,
        ],
      };
    },
  },
};
