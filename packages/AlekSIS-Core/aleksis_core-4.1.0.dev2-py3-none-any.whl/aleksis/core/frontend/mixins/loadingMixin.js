/**
 * This mixin provides generic loading handling.
 * Sets loading state and emits loading event.
 */
export default {
  emits: ["loading"],
  data() {
    return {
      // loading state
      loading: false,
    };
  },
  methods: {
    handleLoading(loading) {
      this.loading = loading;
      /**
       * Emitted on start or finish of loading
       *
       * @property {boolean} status shows whether loading or not
       */
      this.$emit("loading", loading);
    },
  },
};
