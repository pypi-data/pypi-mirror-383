<script setup>
import SecondaryActionButton from "../buttons/SecondaryActionButton.vue";
</script>

<template>
  <v-list-item>
    <div class="d-flex justify-center align-center flex-column full-width">
      <div class="mb-4">
        <v-icon size="large" color="primary">{{ icon }}</v-icon>
      </div>
      <v-list-item-title>
        <slot>
          {{ $t("crud_components.iterator_empty_message.no_data") }}
        </slot>
      </v-list-item-title>
      <v-list-item-action v-if="loadMoreButton">
        <secondary-action-button
          :i18n-key="loadMoreKey"
          @click="$emit('loadMore')"
        />
      </v-list-item-action>
    </div>
  </v-list-item>
</template>
<script>
export default {
  name: "CRUDIteratorEmptyMessage",
  props: {
    icon: {
      type: String,
      default: "mdi-magnify-remove-outline",
    },
    loadMoreButton: {
      type: Boolean,
      default: false,
    },
    loadMoreKey: {
      type: String,
      default: "crud_components.iterator_empty_message.load_more",
    },
  },
  emits: ["loadMore"],
};
</script>
