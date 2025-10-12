<script>
import { admins } from "./admins.graphql";

export default {
  name: "AdminEmailList",
  data() {
    return {
      admins: [],
    };
  },
  apollo: {
    admins: {
      query: admins,
      result({ data }) {
        this.admins = data.systemProperties.admins;
      },
    },
  },
};
</script>

<template>
  <v-list>
    <v-list-item
      v-for="admin in admins"
      :href="`mailto:${admin.email}`"
      :key="admin.email"
    >
      <v-list-item-title>
        {{ admin.name }}
      </v-list-item-title>
      <v-list-item-subtitle>
        {{ admin.email }}
      </v-list-item-subtitle>
    </v-list-item>
  </v-list>
</template>
