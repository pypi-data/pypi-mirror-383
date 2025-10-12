<template>
  <small-container>
    <v-card>
      <v-card-title v-if="pdf">{{ $t("download_pdf.title") }}</v-card-title>
      <v-card-text v-if="pdf" class="text-body-1">
        {{ $t("download_pdf.notice") }}
      </v-card-text>
      <v-card-actions v-if="pdf">
        <v-btn color="primary" variant="text" :href="pdf.file.url" download>
          <v-icon start>mdi-download</v-icon>
          {{ $t("download_pdf.download") }}
        </v-btn>
      </v-card-actions>
      <v-skeleton-loader
        type="article"
        v-if="$apollo.queries.pdf.loading"
      ></v-skeleton-loader>
    </v-card>
  </small-container>
</template>

<script>
import gqlPdf from "./pdf.graphql";

export default {
  name: "DownloadPDF",
  apollo: {
    pdf: {
      query: gqlPdf,
      variables() {
        return {
          id: this.$route.params.id,
        };
      },
    },
  },
  watch: {
    pdf(value) {
      // Automatic redirect
      if (value) {
        window.location.href = value.file.url;
      }
    },
  },
};
</script>
