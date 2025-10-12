<template>
  <v-autocomplete
    v-bind="$attrs"
    hide-no-data
    :items="items"
    :item-title="getItemText"
    item-value="code"
    :loading="loading"
    clearable
  />
</template>

<script>
import queryMixin from "../../../mixins/queryMixin.js";
import { countries } from "./country.graphql";

export default {
  name: "CountryField",
  extends: "v-autocomplete",
  mixins: [queryMixin],
  props: {
    /**
     * The graphQL query used to retrieve the countries.
     */
    gqlQuery: {
      type: Object,
      required: false,
      default: () => countries,
    },
  },
  methods: {
    getItemText(country) {
      return `${country.name} (${country.code})`;
    },
  },
};
</script>
