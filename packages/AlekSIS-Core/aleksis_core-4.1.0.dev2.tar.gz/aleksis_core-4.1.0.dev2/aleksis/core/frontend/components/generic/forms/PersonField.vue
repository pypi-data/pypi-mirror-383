<template>
  <v-autocomplete
    v-bind="$attrs"
    hide-no-data
    :items="combinedItems"
    :item-title="getItemText"
    item-value="id"
    :loading="loading"
    v-model:search="searchString"
    :placeholder="serverSearch ? $t('actions.type_to_search') : ''"
  />
</template>

<script>
import queryMixin from "../../../mixins/queryMixin.js";
import { formPersons } from "./person.graphql";

export default {
  name: "PersonField",
  extends: "v-autocomplete",
  mixins: [queryMixin],
  props: {
    /**
     * The graphQL query used to retrieve the persons.
     */
    gqlQuery: {
      type: Object,
      required: false,
      default: () => formPersons,
    },
    serverSearch: {
      type: Boolean,
      required: false,
      default: false,
    },
    initialItems: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  data() {
    return {
      searchString: "",
    };
  },
  methods: {
    getItemText(person) {
      if (person?.shortName) {
        return `${person.fullName} (${person.shortName})`;
      }
      return person.fullName;
    },
  },
  watch: {
    searchString: {
      handler(newValue) {
        if (this.serverSearch && this.$apollo.queries.items) {
          if (newValue) {
            this.additionalFilters = {
              name: newValue,
            };
            this.$apollo.queries.items.start();
          } else {
            this.items = [];
            this.$apollo.queries.items.stop();
          }
        }
      },
      immediate: true,
    },
  },
  computed: {
    skip() {
      return this.serverSearch && !this.searchString;
    },
    combinedItems() {
      if (this.items) {
        const queryItemIDs = this.items.map((i) => i.id);
        return this.items.concat(
          this.initialItems.filter((i) => !queryItemIDs.includes(i.id)),
        );
      }
      return this.initialItems;
    },
  },
};
</script>
