import loadingMixin from "./loadingMixin.js";

/**
 * This mixin provides generic graphQL mutation handling.
 */
export default {
  mixins: [loadingMixin],
  props: {
    /**
     * The graphQL query this mutation affects.
     * If provided the cached query will be updated.
     * Either use lastQuery from the queryMixin or
     * $apollo.queries[lastQueryName].
     */
    affectedQuery: {
      type: Object,
      required: false,
      default: null,
    },
    /**
     * Key of the affected query data
     * Key can be a single key or nested keys seperated by a '.'
     */
    gqlDataKey: {
      type: String,
      required: false,
      default: "items",
    },
    // itemId is unused in mutateMixin but shared by both
    // createOrPatchMixin & deleteMixin
    /**
     * The item's id property.
     */
    itemId: {
      type: String,
      required: false,
      default: "id",
    },
    /**
     * Method to perform a custom update.
     *
     * This is an alternative way of supplying this method.
     * In case a method is set here, it has higher priority
     * than the one directly submitted to the mutate function.
     */
    customUpdate: {
      type: Function,
      required: false,
      default: undefined,
    },
  },
  computed: {
    mutateProps() {
      return {
        affectedQuery: this.affectedQuery,
        gqlDataKey: this.gqlDataKey,
        itemId: this.itemId,
        customUpdate: this.customUpdate,
      };
    },
  },
};
