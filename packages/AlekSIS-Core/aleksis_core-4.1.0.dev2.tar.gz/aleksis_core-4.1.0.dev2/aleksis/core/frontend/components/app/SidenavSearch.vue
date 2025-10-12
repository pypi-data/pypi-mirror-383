<template>
  <v-autocomplete
    :prepend-icon="'$search'"
    menu-icon=""
    @click:prepend="$router.push(`/search/?q=${q}`)"
    @keydown.enter="$router.push(`/search/?q=${q}`)"
    single-line
    clearable
    :loading="$apollo.queries.searchSnippets.loading"
    id="search"
    type="search"
    enterkeyhint="search"
    :label="$t('actions.search')"
    v-model:search="q"
    flat
    variant="solo"
    hide-no-data
    hide-details
    :menu-props="{ closeOnContentClick: true }"
    :items="searchSnippets"
    auto-select-first
  >
    <template #item="{ item }">
      <v-list-item @click="$router.push(item.obj.absoluteUrl.substring(7))">
        <template #prepend v-if="item.obj.icon">
          <v-icon>{{ "mdi-" + item.obj.icon }}</v-icon>
        </template>

        <v-list-item-title> {{ item.obj.name }}</v-list-item-title>
        <v-list-item-subtitle>{{ item.text }}</v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>

<script>
import gqlSearchSnippets from "./searchSnippets.graphql";

export default {
  name: "SidenavSearch",
  data() {
    return {
      q: "",
      searchSnippets: [],
    };
  },
  apollo: {
    searchSnippets: {
      query: gqlSearchSnippets,
      variables() {
        return {
          q: this.q,
        };
      },
      skip() {
        return !this.q;
      },
      fetchPolicy: "network-only",
    },
  },
};
</script>
