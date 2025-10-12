<script setup>
import { gqlOauthScopes } from "./oauth_application.graphql";
import { useCRUD } from "../../composables/crud/useCRUD";
const choices = useCRUD({ query: gqlOauthScopes });
</script>

<template>
  <span>
    <v-autocomplete
      :loading="choices.queryLoading.value"
      v-bind="{ ...$attrs, items: choices.queryItems.value }"
      multiple
      item-title="description"
      item-value="name"
    />
  </span>
</template>
