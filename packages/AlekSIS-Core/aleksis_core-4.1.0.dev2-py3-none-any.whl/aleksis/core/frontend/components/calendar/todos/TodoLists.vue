<template>
  <div>
    <v-row class="overflow-x-auto flex-nowrap slide-n-snap-x-container">
      <v-col
        v-for="feed in calendar.calendarFeeds"
        :key="feed.name"
        class="slide-n-snap-contained"
        cols="12"
        :sm="Math.max(6, 12 / calendar.calendarFeeds.length)"
      >
        <v-card>
          <v-card-title>
            {{ feed.verboseName }}
          </v-card-title>
          <v-list lines="two">
            <template
              v-for="event in getNonCompletedTodos(feed.events)"
              :key="event.uid"
            >
              <component
                :is="listItemComponentForFeed(feed.name)"
                @refresh-calendar="refresh()"
                :selected-event="event"
              />
            </template>
            <v-list-group>
              <template #activator>
                <v-list-item-title>{{
                  $t("calendar.todos.show_completed", {
                    count: getCompletedTodos(feed.events).length,
                  })
                }}</v-list-item-title>
              </template>

              <template
                v-for="event in getCompletedTodos(feed.events)"
                :key="event.uid"
              >
                <component
                  :is="listItemComponentForFeed(feed.name)"
                  @refresh-calendar="refresh()"
                  :selected-event="event"
                />
              </template>
            </v-list-group>
          </v-list>

          <v-card-actions v-if="formComponentForFeed(feed.name)">
            <component
              :is="formComponentForFeed(feed.name)"
              @refresh-calendar="refresh()"
            >
              <template #activator="{ on, attrs }">
                <create-button
                  v-bind="attrs"
                  v-on="on"
                  color="secondary"
                  outlined
                />
              </template>
            </component>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import CreateButton from "../../generic/buttons/CreateButton.vue";

import { useCalendar } from "../calendarMixin.js";

import { defineProps, toRef, onMounted } from "vue";

import {
  calendarFeedFormComponents,
  calendarFeedListItemComponents,
} from "aleksisAppImporter";

const props = defineProps({
  calendarFeeds: {
    type: Array,
    required: false,
    default: () => [],
  },
  params: {
    type: Object,
    required: false,
    default: null,
  },
});

const { calendar, fetch, refresh } = useCalendar(
  toRef(props, "calendarFeeds"),
  toRef(props, "params"),
);

function formComponentForFeed(feedName) {
  if (
    calendar.calendarFeeds &&
    feedName &&
    Object.keys(calendarFeedFormComponents).includes(feedName + "form")
  ) {
    return calendarFeedFormComponents[feedName + "form"];
  }
  return null;
}
function listItemComponentForFeed(feedName) {
  if (
    calendar.calendarFeeds &&
    feedName &&
    Object.keys(calendarFeedListItemComponents).includes(feedName + "listitem")
  ) {
    return calendarFeedListItemComponents[feedName + "listitem"];
  }
  return null;
}
function getNonCompletedTodos(events) {
  return events.filter((e) => e.percentComplete !== 100);
}
function getCompletedTodos(events) {
  return events.filter((e) => e.percentComplete === 100);
}

onMounted(fetch);
</script>

<style>
.slide-n-snap-x-container {
  scroll-snap-type: x mandatory;
  /* scroll-snap-stop: always; */
}
.slide-n-snap-y-container {
  scroll-snap-type: y mandatory;
  /* scroll-snap-stop: always; */
}
.slide-n-snap-contained {
  scroll-snap-align: start;
}
</style>
