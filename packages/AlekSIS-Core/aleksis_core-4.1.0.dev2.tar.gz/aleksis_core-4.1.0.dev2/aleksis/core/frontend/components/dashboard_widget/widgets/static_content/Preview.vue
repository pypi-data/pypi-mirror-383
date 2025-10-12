<script>
import previewMixin from "../previewMixin";

export default {
  name: "Preview",
  mixins: [previewMixin],
};
</script>

<template>
  <v-card class="fullsize">
    <v-card-title>
      {{ widget.title }}
    </v-card-title>

    <v-card-text>
      <v-skeleton-loader boilerplate type="paragraph@2" />
    </v-card-text>
  </v-card>
</template>
