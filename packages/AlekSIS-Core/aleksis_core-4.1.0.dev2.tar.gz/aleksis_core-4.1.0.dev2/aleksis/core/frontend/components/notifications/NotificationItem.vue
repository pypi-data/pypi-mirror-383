<script setup>
import { reactive } from "vue";
import { markNotificationRead } from "./markNotificationRead.graphql";

const mutation = reactive(markNotificationRead);
</script>

<template>
  <ApolloMutation
    :mutation="mutation"
    :variables="{ id: this.notification.id }"
  >
    <template #default="{ mutate, loading, error }">
      <v-list-item
        :active="!notification.read"
        :title="notification.title"
        :subtitle="notification.description"
      >
        <template #prepend>
          <v-icon :color="notification.read ? 'grey' : 'primary'">
            mdi-{{ notification.icon.toLowerCase().replaceAll("_", "-") }}
          </v-icon>
        </template>

        <v-list-item-subtitle class="text-caption font-weight-regular">
          <v-chip size="x-small" variant="outlined">{{
            notification.sender
          }}</v-chip>
          ·
          <v-tooltip location="bottom">
            <template #activator="{ props }">
              <span v-bind="props">{{
                $d(
                  $parseISODate(notification.created),
                  dateFormat($parseISODate(notification.created)),
                )
              }}</span>
            </template>
            <span>{{ $d($parseISODate(notification.created), "long") }}</span>
          </v-tooltip>
        </v-list-item-subtitle>

        <template #append>
          <icon-button
            icon-text="mdi-email-outline"
            color="secondary"
            i18n-key="notifications.mark_as_read"
            v-if="!notification.read"
            @click="mutate"
          />

          <icon-button
            icon-text="mdi-open-in-new"
            color="accent"
            i18n-key="notifications.more_information"
            :href="notification.link"
            v-if="notification.link"
          />
        </template>
      </v-list-item>
    </template>
  </ApolloMutation>
</template>

<script>
import { DateTime } from "luxon";

export default {
  props: {
    notification: {
      type: Object,
      required: true,
    },
  },
  methods: {
    dateFormat(date) {
      let now = DateTime.now();
      if (now.hasSame(date, "day")) {
        return "timeOnly";
      } else {
        return "short";
      }
    },
  },
};
</script>
