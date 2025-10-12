<script setup>
import { algorithmChoices } from "./oauth";
</script>

<template>
  <v-autocomplete
    v-bind="$attrs"
    :items="algorithmChoices"
    :item-title="(item) => $t(item.title)"
  />
</template>
