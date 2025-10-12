<script>
import previewMixin from "../previewMixin";

export default {
  name: "Preview",
  mixins: [previewMixin],
};
</script>

<template>
  <v-card class="fullsize d-flex flex-column">
    <v-skeleton-loader boilerplate type="image" class="flex-grow-1" />

    <v-card-actions>
      <v-btn color="primary" variant="text" disabled>
        {{ widget.title }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
