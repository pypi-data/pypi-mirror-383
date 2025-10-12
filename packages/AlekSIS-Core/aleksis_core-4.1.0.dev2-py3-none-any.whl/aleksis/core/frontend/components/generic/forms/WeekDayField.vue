<template>
  <v-autocomplete
    v-bind="$attrs"
    :items="items"
    item-title="text"
    item-value="valueInt"
  ></v-autocomplete>
</template>

<script setup>
import { useI18n } from "../../../composables/app/useI18n";

const { t } = useI18n();
const items = [
  {
    valueInt: 0,
    text: t("weekdays.0"),
  },
  {
    valueInt: 1,
    text: t("weekdays.1"),
  },
  {
    valueInt: 2,
    text: t("weekdays.2"),
  },
  {
    valueInt: 3,
    text: t("weekdays.3"),
  },
  {
    valueInt: 4,
    text: t("weekdays.4"),
  },
  {
    valueInt: 5,
    text: t("weekdays.5"),
  },
  {
    valueInt: 6,
    text: t("weekdays.6"),
  },
];
</script>
