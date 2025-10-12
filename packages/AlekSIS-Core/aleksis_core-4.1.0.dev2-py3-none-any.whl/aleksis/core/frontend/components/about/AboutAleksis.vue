<!-- General information about AlekSIS as a whole -->
<script setup>
import Mascot from "../generic/mascot/Mascot.vue";
</script>

<template>
  <v-row class="mb-3">
    <v-col cols="12">
      <v-card>
        <v-row>
          <v-col cols="12" md="9" class="d-flex flex-column">
            <v-card-title>{{ $t("about.about_aleksis") }}</v-card-title>
            <v-card-text>
              <p class="text-body-1">
                {{ $t("about.about_aleksis_1") }}
              </p>
              <p class="text-body-1">
                {{ $t("about.about_aleksis_2") }}
              </p>
            </v-card-text>
            <v-spacer />
            <v-card-actions>
              <v-btn variant="text" color="primary" href="https://aleksis.org/">
                {{ $t("about.website_of_aleksis") }}
              </v-btn>
              <v-btn
                variant="text"
                color="primary"
                href="https://edugit.org/AlekSIS/"
              >
                {{ $t("about.source_code") }}
              </v-btn>
            </v-card-actions>
          </v-col>
          <v-col cols="12" md="3">
            <mascot />
          </v-col>
        </v-row>
      </v-card>
    </v-col>
    <v-col cols="12">
      <v-card class="d-flex flex-column">
        <v-card-title>{{ $t("about.licence_information") }}</v-card-title>
        <v-card-text>
          <p>
            {{ $t("about.licence_information_1") }}
          </p>
          <p>
            <v-chip color="green" size="small">
              {{ $t("about.free_open_source_licence") }}
            </v-chip>
            <v-chip color="orange" size="small">
              {{ $t("about.other_licence") }}
            </v-chip>
          </p>
        </v-card-text>
        <v-spacer />
        <v-card-actions>
          <v-btn variant="text" color="primary" href="https://eupl.eu">
            {{ $t("about.full_licence_text") }}
          </v-btn>
          <v-btn
            variant="text"
            color="primary"
            href="https://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers"
          >
            {{ $t("about.more_information_eupl") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: "AboutAleksis",
};
</script>

<style scoped></style>
