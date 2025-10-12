import mutateMixin from "./mutateMixin.js";
import createOrPatchPropsMixin from "./createOrPatchPropsMixin";

/**
 * This mixin provides item creation or update via graphQL.
 */
export default {
  mixins: [mutateMixin, createOrPatchPropsMixin],
  computed: {
    provideMutation() {
      return this.isCreate ? this.gqlCreateMutation : this.gqlPatchMutation;
    },
  },
  methods: {
    /**
     * Create or patch an array of items
     * Create if isCreate and patch otherwise.
     * This requires gql*Mutation and get*Data (Can use default)
     * itemId is the item's id property.
     *
     * @param {Array} items
     * @param {string} itemId
     */
    createOrPatch(items, itemId) {
      itemId = itemId || this.itemId || "id";
      this.mutate(
        this.provideMutation,
        {
          input: items.map(
            this.isCreate ? this.getCreateData : this.getPatchData,
          ),
        },
        this.handleUpdateAfterCreateOrPatch(itemId, this.isCreate),
      );
    },
    /**
     * Update the cached gqlQuery to reflect a successful create or patch
     * This is a no op if no gqlQuery was provided.
     */
    handleUpdateAfterCreateOrPatch(itemId, wasCreate) {
      return (cached, incoming) => {
        if (wasCreate) {
          // Just append newly created objects
          return [...cached, ...incoming];
        } else {
          for (const object of incoming) {
            // Replace the updated objects
            const index = cached.findIndex((o) => o[itemId] === object[itemId]);
            cached[index] = object;
          }
          return cached;
        }
      };
    },
  },
};
