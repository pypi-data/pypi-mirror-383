<script>
import previewMixin from "../previewMixin";

export default {
  name: "Preview",
  mixins: [previewMixin],
};
</script>

<template>
  <v-card class="fullsize">
    <!-- eslint-disable-next-line vue/no-v-text-v-html-on-component -->
    <v-card-title v-text="widget.title" />
    <v-card-text>
      <v-skeleton-loader boilerplate type="text@8" />
    </v-card-text>
  </v-card>
</template>
