<script>
import sexChoiceMixin from "../../../mixins/sexChoiceMixin";

export default {
  name: "SexSelect",
  mixins: [sexChoiceMixin],
};
</script>

<template>
  <v-autocomplete v-bind="$attrs" :items="sexChoices">
    <template #selection="{ item }">
      <v-icon start>{{ item.icon }}</v-icon>
      <span>{{ item.text }}</span>
    </template>

    <template #item="{ item }">
      <v-list-item v-bind="props">
        <template #prepend>
          <v-icon>{{ item.icon }}</v-icon>
        </template>

        <v-list-item-title>{{ item.text }}</v-list-item-title>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>
