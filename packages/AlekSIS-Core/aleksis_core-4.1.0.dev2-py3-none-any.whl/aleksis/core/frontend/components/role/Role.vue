<script setup>
import CRUDProvider from "../generic/crud/CRUDProvider.vue";
import ColorField from "../generic/forms/ColorField.vue";
import RoleChip from "./RoleChip.vue";
// TODO: Editing a color does send a proper mutation but leads to an unknown graphql error.
</script>

<template>
  <c-r-u-d-provider :object-schema="{ type: 'RoleType' }">
    <template #field.name="{ item }">
      <role-chip :role="item" />
    </template>

    <template #item.fgColor="{ item }">
      <v-chip :color="item.fgColor" variant="outlined">
        {{ item.fgColor }}
      </v-chip>
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #fgColor.field="props">
      <color-field v-bind="props" />
    </template>

    <template #item.bgColor="{ item }">
      <v-chip :color="item.bgColor" variant="outlined">
        {{ item.bgColor }}
      </v-chip>
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #bgColor.field="props">
      <color-field v-bind="props" />
    </template>
  </c-r-u-d-provider>
</template>
