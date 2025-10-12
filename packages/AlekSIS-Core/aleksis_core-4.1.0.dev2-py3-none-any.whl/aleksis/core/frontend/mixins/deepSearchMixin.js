/**
 * Mixin that provides a search function for searching deep properties of objects
 */
export default {
  props: {
    useDeepSearch: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  computed: {
    /**
     * Search function. Has to be explicitly activated using the useDeepSearch prop!
     *
     * @return {undefined|function(any[], string): any[]}
     */
    deepSearch() {
      if (!this.useDeepSearch) {
        return undefined;
      }

      /**
       *
       * @param {any[]} items
       * @param {string} search
       * @return {any[]}
       */
      function search(items, search) {
        if (!search || !items.length) return items;
        search = (search || "").trim().toLowerCase();
        if (!search) return items;

        return items.filter((item) =>
          JSON.stringify(item).toLowerCase().includes(search),
        );
      }

      return search;
    },
  },
};
