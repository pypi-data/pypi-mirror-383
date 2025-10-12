<script setup>
import BaseCalendarFeedListItem from "./BaseCalendarFeedListItem.vue";
</script>

<template>
  <base-calendar-feed-list-item v-bind="$props" />
</template>

<script>
import calendarFeedListItemMixin from "../../mixins/calendarFeedListItem.js";

export default {
  name: "GenericCalendarFeedListItem",
  mixins: [calendarFeedListItemMixin],
};
</script>
