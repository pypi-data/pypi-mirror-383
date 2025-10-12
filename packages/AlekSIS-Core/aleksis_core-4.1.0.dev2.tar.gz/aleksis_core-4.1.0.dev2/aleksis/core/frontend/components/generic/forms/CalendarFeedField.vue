<template>
  <v-autocomplete
    v-bind="$attrs"
    hide-no-data
    :items="items.calendarFeeds"
    item-title="verboseName"
    item-value="name"
    :loading="loading"
  />
</template>

<script>
import queryMixin from "../../../mixins/queryMixin.js";
import { fieldCalendarFeeds } from "./calendarFeeds.graphql";

export default {
  name: "CalendarFeedField",
  extends: "v-autocomplete",
  mixins: [queryMixin],
  props: {
    /**
     * The graphQL query used to retrieve the calendar feeds.
     */
    gqlQuery: {
      type: Object,
      required: false,
      default: () => fieldCalendarFeeds,
    },
  },
};
</script>
