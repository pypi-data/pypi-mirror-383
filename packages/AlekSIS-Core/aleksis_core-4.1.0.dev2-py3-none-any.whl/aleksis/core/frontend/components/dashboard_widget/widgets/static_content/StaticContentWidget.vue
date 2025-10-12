<script>
import widgetMixin from "../widgetMixin";

export default {
  name: "StaticContentWidget",
  mixins: [widgetMixin],
};
</script>

<template>
  <v-card>
    <v-card-title>
      {{ widget.title }}
    </v-card-title>
    <!-- eslint-disable-next-line vue/no-v-text-v-html-on-component -->
    <v-card-text v-html="widget.content" />
  </v-card>
</template>
