<template>
  <span>
    <span v-if="value">
      {{ $t(lookupChoiceTitle(algorithmChoices, value)) }}
    </span>
    <span v-else>–</span>
  </span>
</template>

<script setup>
import { algorithmChoices } from "./oauth";
import { defineProps } from "vue";
import { lookupChoiceTitle } from "../../util/lookups";

const { value } = defineProps({
  value: {
    type: Object,
    default: undefined,
  },
});
</script>
