<!-- This should become a foreign-key-field as soon as the groups page is moved to graphql. -->
<template>
  <v-autocomplete
    v-bind="$attrs"
    hide-no-data
    :items="items"
    item-title="shortName"
    item-value="id"
    :loading="loading"
  />
</template>

<script>
import queryMixin from "../../../mixins/queryMixin.js";
import { formGroups } from "./group.graphql";

export default {
  name: "GroupField",
  extends: "v-autocomplete",
  mixins: [queryMixin],
  props: {
    /**
     * The graphQL query used to retrieve the groups.
     */
    gqlQuery: {
      type: Object,
      required: false,
      default: () => formGroups,
    },
  },
};
</script>
