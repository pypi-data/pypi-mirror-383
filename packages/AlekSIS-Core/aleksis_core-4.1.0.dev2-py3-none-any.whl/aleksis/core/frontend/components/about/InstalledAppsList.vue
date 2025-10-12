<!-- List of all installed AlekSIS apps, as discovered from the server -->

<template>
  <div>
    <v-row v-if="$apollo.queries.installedApps.loading">
      <v-col
        v-for="idx in 3"
        :key="idx"
        cols="12"
        md="6"
        lg="6"
        xl="4"
        class="d-flex align-stretch"
      >
        <v-card class="d-flex flex-column flex-grow-1 pa-4">
          <v-skeleton-loader
            type="heading, actions, text@5"
          ></v-skeleton-loader>
        </v-card>
      </v-col>
    </v-row>
    <v-row v-if="installedApps">
      <installed-app-card
        v-for="app in installedApps"
        :key="app.name"
        :app="app"
      />
    </v-row>
  </div>
</template>

<script>
import InstalledAppCard from "./InstalledAppCard.vue";
import gqlInstalledApps from "./installedApps.graphql";
export default {
  name: "InstalledAppsList",
  components: { InstalledAppCard },
  apollo: {
    installedApps: {
      query: gqlInstalledApps,
    },
  },
};
</script>
