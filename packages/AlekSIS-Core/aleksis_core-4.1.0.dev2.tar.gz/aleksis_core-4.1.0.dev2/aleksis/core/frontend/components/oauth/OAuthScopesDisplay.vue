<template>
  <span>
    <v-chip v-for="scope in value" :key="scope">
      {{
        lookupChoiceText(choices.queryItems.value, scope, "name", "description")
      }}
    </v-chip>
  </span>
</template>

<script setup>
import { defineProps } from "vue";
import { gqlOauthScopes } from "./oauth_application.graphql";
import { useCRUD } from "../../composables/crud/useCRUD";
const choices = useCRUD({ query: gqlOauthScopes });

const { value } = defineProps({
  value: {
    type: Array,
    default: undefined,
  },
});

function lookupChoiceText(
  choices,
  value,
  valueKey = "value",
  textKey = "title",
) {
  return (choices.find((choice) => choice[valueKey] === value) || {
    [textKey]: value,
  })[textKey];
}
</script>
