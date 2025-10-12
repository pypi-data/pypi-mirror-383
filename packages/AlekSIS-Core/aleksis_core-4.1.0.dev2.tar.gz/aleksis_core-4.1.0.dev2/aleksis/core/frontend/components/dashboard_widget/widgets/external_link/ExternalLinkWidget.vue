<script>
import widgetMixin from "../widgetMixin";

export default {
  name: "ExternalLinkWidget",
  mixins: [widgetMixin],
};
</script>

<template>
  <v-card class="d-flex flex-column">
    <v-img :src="widget.iconUrl" :alt="widget.title" />

    <v-card-actions>
      <v-btn color="primary" variant="text" :href="widget.url" target="_blank">
        {{ widget.title }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
