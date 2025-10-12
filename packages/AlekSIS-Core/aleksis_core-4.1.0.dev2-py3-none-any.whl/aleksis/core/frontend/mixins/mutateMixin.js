import loadingMixin from "./loadingMixin.js";
import mutatePropsMixin from "./mutatePropsMixin";

/**
 * This mixin provides generic graphQL mutation handling.
 */
export default {
  mixins: [loadingMixin, mutatePropsMixin],
  // update & save come from DialogObjectForm
  // save could be success as well but keeping it backwards compatible
  // for now
  emits: ["update", "save"],
  computed: {
    // Expand the affectedQuery
    expandedQuery() {
      if (!this.affectedQuery) {
        return false;
      }
      const variables = this.affectedQuery.previousVariablesJson
        ? JSON.parse(this.affectedQuery.previousVariablesJson)
        : {};

      return {
        ...this.affectedQuery.options,
        variables,
      };
    },
  },
  methods: {
    /**
     * Do a graphQL mutation with variables
     *
     * Provide updateStore to update the cached data for affectedQuery with
     * the incoming data.
     *
     * @param {Object} mutation
     * @param {Object} variables
     * @param {Function} updateStore
     * @param {Object} additionalArgs additional arguments passed to apollo mutate function options
     */
    mutate(
      mutation,
      variables,
      updateStore = (cached, incoming) => {},
      additionalArgs = {},
    ) {
      this.handleLoading(true);

      if (this.customUpdate) {
        updateStore = this.customUpdate;
      }

      this.$apollo
        .mutate({
          mutation: mutation,
          variables: variables,
          update: (store, data) => {
            // TODO: Is data transformed properly?
            // Current implemented for create | patch
            // What does it return for delete?
            data = data.data[mutation.definitions[0].name.value].items;

            // Update cached data
            if (this.expandedQuery) {
              // Read the data from cache for query
              const cachedQuery = store.readQuery(this.expandedQuery);
              if (cachedQuery) {
                // Update the store
                this.setKeysRecursive(
                  this.gqlDataKey,
                  cachedQuery,
                  updateStore(
                    this.getKeysRecursive(this.gqlDataKey, cachedQuery),
                    data,
                  ),
                );
                // Write data back to the cache
                store.writeQuery({ ...this.expandedQuery, data: cachedQuery });
              }
            }

            /**
             * Emits the store and data when graphQL updates
             * Use this to update the cached query if  affectedQuery or
             * updateStore was not provided
             *
             * @property {object} store
             * @property {object} updated object
             */
            this.$emit("update", store, data);
            this.onUpdate?.(store, data);
          },
          ...additionalArgs,
        })
        .then((data) => {
          /**
           * Emits the items of a successful graphQL mutation
           * If affectedQuery was provided the items are already updated in the cache.
           *
           * @property {object} data
           */
          this.$emit(
            "save",
            data.data[mutation.definitions[0].name.value].items,
          );
          this.onSave(data.data[mutation.definitions[0].name.value].items);
        })
        .catch((error) => {
          this.handleMutationError(error);
        })
        .finally(() => {
          this.handleLoading(false);
        });
    },
    /**
     * This is called when the graphQL mutation updated the store.
     * This is a hook, as vue3 remove the this.$on listener
     * @param store The store
     * @param data The data returned from the mutation
     */
    onupdate(store, data) {},
    /**
     * This is called when the graphQL mutation was successful.
     * This is a hook, as vue3 remove the this.$on listener
     * @param data The data returned from the mutation
     */
    onSave(data) {},
  },
};
