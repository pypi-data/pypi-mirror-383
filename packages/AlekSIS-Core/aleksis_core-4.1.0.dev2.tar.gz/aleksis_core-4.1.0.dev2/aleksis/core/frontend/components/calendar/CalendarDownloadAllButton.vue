<script>
export default {
  name: "CalendarDownloadAllButton",
  props: {
    url: {
      type: String,
      required: true,
    },
  },
};
</script>
<template>
  <v-btn variant="flat" block :href="url">
    <v-icon start>mdi-download-outline</v-icon>
    {{ $t("calendar.download_all") }}
  </v-btn>
</template>
