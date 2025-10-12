/**
 * This mixin provides props for the query mixin.
 */
export default {
  props: {
    /**
     * The graphQL query
     */
    gqlQuery: {
      type: [Function, Object],
      required: true,
    },
    /**
     * Optional arguments to graphQL query
     */
    // UPDATE NOTICE: Name change from additionalQueryArgs (prop was so far not used anyway)
    gqlAdditionalQueryArgs: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    /**
     * OrderBy directive used in the graphQL query
     */
    gqlOrderBy: {
      type: Array,
      required: false,
      default: () => [],
    },
    /**
     * Filter object used in the graphQL query
     */
    gqlFilters: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    /**
     * Transform function for the data returned by the query
     */
    getGqlData: {
      type: Function,
      required: false,
      default: (item) => item,
    },
    /**
     * Key of the desired data payload
     * Key can be a single key or nested keys seperated by a '.'
     */
    gqlDataKey: {
      type: String,
      required: false,
      default: "items",
    },
    /**
     * Key of the apollo query
     * Key can be a single key or nested keys seperated by a '.'
     */
    gqlQueryKey: {
      type: String,
      required: false,
      default: "items",
    },
  },
  computed: {
    queryProps() {
      return {
        gqlQuery: this.gqlQuery,
        gqlAdditionalQueryArgs: this.gqlAdditionalQueryArgs,
        gqlOrderBy: this.gqlOrderBy,
        gqlFilters: this.gqlFilters,
        getGqlData: this.getGqlData,
        gqlDataKey: this.gqlDataKey,
        gqlQueryKey: this.gqlQueryKey,
      };
    },
  },
};
