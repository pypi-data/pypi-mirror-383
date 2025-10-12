<script setup>
import { clientTypeChoices } from "./oauth";
</script>

<template>
  <v-autocomplete
    v-bind="$attrs"
    :items="clientTypeChoices"
    :item-title="(item) => $t(item.title)"
  />
</template>
