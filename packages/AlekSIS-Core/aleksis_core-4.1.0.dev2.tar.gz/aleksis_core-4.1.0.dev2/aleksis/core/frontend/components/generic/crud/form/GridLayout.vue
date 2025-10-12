<script setup>
import Field from "./Field.vue";

const props = defineProps({
  /**
   * field -> { cols, field }
   */
  fields: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <v-container>
    <v-row align="end">
      <v-col
        v-for="(field, name) in props.fields"
        cols="12"
        :sm="field.cols"
        :key="name"
      >
        <field :field="field.field" />
      </v-col>
    </v-row>
  </v-container>
</template>
