import queryPropsMixin from "./queryPropsMixin";
import mutatePropsMixin from "./mutatePropsMixin";

/**
 * This mixin provides shared crud props.
 */
export default {
  mixins: [mutatePropsMixin, queryPropsMixin],
  props: {
    /**
     * Enable editing of items
     * via the create component (defaults to DialogObjectForm)
     * @values true, false
     */
    enableEdit: {
      type: Boolean,
      required: false,
      default: true,
    },
    // create/patch
    /**
     * An array of objects that each describe an item field
     * This prop is a superset of the v-data-table prop with the same
     * name.
     * Used here for the create component & describes the CRUDList
     * Additional fields are documented in the example:
     *
     * @example [
     *            {
     *              // Required
     *              text: "displayed name",
     *              value: "internal name",
     *              // See v-data-table api for more.
     *              // CRUDBar specific optional fields:
     *              disableEdit: true,  // This is a non editable colum
     *              // DialogObjectForm specific optional fields:
     *              // Amount of columns used for this field
     *              // from a total of 12
     *              cols: 6,
     *              // CRUDList and CRUDIterator specific optional fields:
     *              hidden: true,       // Hide this colum
     *              orderKey: "field used for odering"
     *            },
     *            ...
     *          ]
     */
    headers: {
      type: Array,
      required: false,
      default: () => [],
    },
    /**
     * Enable creation of items
     * via the create component (defaults to DialogObjectForm)
     * This shows a create button in the table header.
     * @values true, false
     */
    enableCreate: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * Show create button of the default create component
     * (DialogObjectForm)
     * @values true, false
     */
    showCreate: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * Default item used for creation
     * This is required if enableCreate is true and
     * the default create component slot is used.
     */
    defaultItem: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    /**
     * Enable deletion of items
     * via the delete component (defaults to DeleteDialog)
     * @values true, false
     */
    enableDelete: {
      type: Boolean,
      required: false,
      default: true,
    },

    // filter
    /**
     * Enable filtering the items
     * This lets the user choose a filter and applies it to the graphQL query.
     * @values true, false
     */
    enableFilter: {
      type: Boolean,
      required: false,
      default: false,
    },
    // search
    /**
     * Enable the search input
     * @values true, false
     */
    enableSearch: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * Lock updating the items
     * Deactivates changing the filter, search, the items themselves (create, edit, delete) and selecting actions.
     * This only prohibits the user from updating the items, props can still influence them.
     * @values true, false
     */
    lock: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  computed: {
    /**
     * Combination of all crud props to pass down to child components
     */
    crudProps() {
      return {
        enableEdit: this.enableEdit,
        enableCreate: this.enableCreate,
        enableDelete: this.enableDelete,
        enableFilter: this.enableFilter,
        enableSearch: this.enableSearch,
        showCreate: this.showCreate,
        headers: this.headers,
        defaultItem: this.defaultItem,
        lock: this.lock,
        ...this.queryProps,
        ...this.mutateProps,
      };
    },
  },
};
