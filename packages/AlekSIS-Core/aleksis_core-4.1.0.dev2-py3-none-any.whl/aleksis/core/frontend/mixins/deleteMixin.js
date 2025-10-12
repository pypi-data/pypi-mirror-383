import mutateMixin from "./mutateMixin.js";

/**
 * This mixin provides item deletion via graphQL.
 */
export default {
  mixins: [mutateMixin],
  props: {
    /**
     * The graphQL delete mutation
     *
     * BREAKING CHANGE: This used to delete only single items (variable: id)
     * Now it deletes multiple items (variable: ids) as did
     * gqlDeleteMultipleMutation previously.
     * To delete a single item pass id: [item].
     */
    gqlDeleteMutation: {
      type: Object,
      required: false,
      default: undefined,
    },
  },
  methods: {
    /**
     * Delete an array of items
     * Using delete requires gqlDeleteMutation.
     * itemId is the item's id property.
     *
     * @param {Array} items
     * @param {string} itemId
     */
    delete(items, itemId) {
      itemId = itemId || this.itemId || "id";
      const ids = items.map((item) => item[itemId]);
      this.mutate(
        this.gqlDeleteMutation,
        { ids: ids },
        this.handleUpdateAfterDelete(ids, itemId),
      );
    },
    /**
     * Update the cached gqlQuery to reflect a successful deletion
     * This is a no op if no gqlQuery was provided.
     */
    handleUpdateAfterDelete(ids, itemId) {
      // This could probably use incoming data for ids too.
      return (cached, incoming) => {
        for (const id of ids) {
          // Remove item from cached data
          const index = cached.findIndex((o) => o[itemId] === id);
          cached.splice(index, 1);
        }
        return cached;
      };
    },
  },
};
