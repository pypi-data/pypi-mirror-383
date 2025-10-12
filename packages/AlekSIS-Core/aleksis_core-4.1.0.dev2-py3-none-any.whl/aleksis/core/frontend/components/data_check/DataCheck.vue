<script setup>
import PrimaryActionButton from "../generic/buttons/PrimaryActionButton.vue";
import SecondaryActionButton from "../generic/buttons/SecondaryActionButton.vue";
</script>

<template>
  <div>
    <template v-if="$apollo.queries.dataChecks.loading">
      <v-skeleton-loader type="card,card,card"></v-skeleton-loader>
    </template>
    <template v-else>
      <v-card
        v-if="unsolvedDataCheckResults.length"
        class="mb-4"
        :loading="$apollo.queries.dataCheckResults.loading"
      >
        <v-card-title>
          <v-icon class="mr-2" color="warning">$warning</v-icon>
          {{ $t("administration.data_check.problems_detected.title") }}
          <v-spacer />
          <ApolloMutation :mutation="gqlSolveDataCheckResult">
            <template #default="{ mutate, loading, error }">
              <primary-action-button
                :loading="loading"
                @click="runDataChecks(mutate)"
                i18n-key="administration.data_check.check_again"
              />
            </template>
          </ApolloMutation>
        </v-card-title>
        <v-card-text>
          {{ $t("administration.data_check.problems_detected.text") }}
        </v-card-text>
        <v-card-title>
          {{ $t("administration.data_check.detected_problems.title") }}
        </v-card-title>
        <v-data-table
          :headers="dataCheckResultHeaders"
          :items="unsolvedDataCheckResults"
          :items-per-page="-1"
          hide-default-footer
          :loading="$apollo.queries.dataCheckResults.loading"
        >
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.relatedObject.absoluteUrl="{ item }">
            <secondary-action-button
              v-if="item.relatedObject.absoluteUrl"
              :href="item.relatedObject.absoluteUrl"
              i18n-key="administration.data_check.detected_problems.show_object"
              target="_blank"
              icon-text="mdi-open-in-new"
            />
            <div v-else>–</div>
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.relatedCheck.solveOptions="{ item }">
            <template v-if="item.relatedCheck.solveOptions.length">
              <ApolloMutation
                v-for="solveOption in item.relatedCheck.solveOptions"
                :key="solveOption.name"
                :mutation="gqlSolveDataCheckResult"
                :variables="{ result: item.id, solveOption: solveOption.name }"
                :refetch-queries="dataCheckResultsQuery"
              >
                <template #default="{ mutate, loading, error }">
                  <v-btn color="primary" :loading="loading" @click="mutate">
                    {{ solveOption.verboseName }}
                  </v-btn>
                </template>
              </ApolloMutation>
            </template>
            <div v-else>–</div>
          </template>
        </v-data-table>
      </v-card>
      <v-card v-else class="mb-4">
        <v-card-title>
          <v-icon class="mr-2" color="success">$success</v-icon>
          {{ $t("administration.data_check.no_problems_detected.title") }}
          <v-spacer />
          <ApolloMutation :mutation="gqlRunDataChecks">
            <template #default="{ mutate, loading, error }">
              <primary-action-button
                :loading="loading"
                @click="runDataChecksMutation(mutate)"
                i18n-key="administration.data_check.check_again"
              />
            </template>
          </ApolloMutation>
        </v-card-title>
        <v-card-text>{{
          $t("administration.data_check.no_problems_detected.text")
        }}</v-card-text>
      </v-card>
      <v-card class="mb-4" :loading="$apollo.queries.dataChecks.loading">
        <v-card-title>
          {{ $t("administration.data_check.registered_checks.title") }}
        </v-card-title>
        <v-card-text>
          {{ $t("administration.data_check.registered_checks.help_text") }}
        </v-card-text>
        <v-list density="compact">
          <template
            v-for="(check, index) in dataChecks"
            :key="`list-item-${index}`"
          >
            <v-list-item prepend-icon="$success" :title="check.verboseName" />
            <v-divider
              v-if="index < dataChecks.length - 1"
              :key="`divider-${index}`"
              inset
            />
          </template>
        </v-list>
      </v-card>
    </template>
  </div>
</template>

<script>
import {
  gqlDataChecks,
  gqlDataCheckResults,
  runDataChecks,
  solveDataCheckResult,
} from "./dataCheck.graphql";

export default {
  name: "DataCheck",
  apollo: {
    dataChecks: {
      query: gqlDataChecks,
      fetchPolicy: "network-only",
    },
    dataCheckResults: {
      query: gqlDataCheckResults,
      fetchPolicy: "network-only",
    },
  },
  data() {
    return {
      dataCheckResultHeaders: [
        {
          text: this.$t(
            "administration.data_check.detected_problems.headers.id",
          ),
          value: "id",
        },
        {
          text: this.$t(
            "administration.data_check.detected_problems.headers.related_model",
          ),
          value: "relatedObject.classVerboseName",
        },
        {
          text: this.$t(
            "administration.data_check.detected_problems.headers.related_object",
          ),
          value: "relatedObject.instanceVerboseName",
        },
        {
          text: this.$t(
            "administration.data_check.detected_problems.headers.problem",
          ),
          value: "relatedCheck.problemName",
        },
        {
          text: this.$t(
            "administration.data_check.detected_problems.headers.show_details",
          ),
          value: "relatedObject.absoluteUrl",
        },
        {
          text: this.$t(
            "administration.data_check.detected_problems.headers.solve_options",
          ),
          value: "relatedCheck.solveOptions",
        },
      ],
      dataCheckResults: [],
      dataChecks: [],
      gqlSolveDataCheckResult: solveDataCheckResult,
      gqlRunDataChecks: runDataChecks,
    };
  },
  computed: {
    unsolvedDataCheckResults() {
      return this.dataCheckResults.filter((r) => r.solved === false);
    },
    dataCheckResultsQuery() {
      return () => [{ query: gqlDataCheckResults }];
    },
  },
  methods: {
    runDataChecksMutation(mutate) {
      this.$activateFrequentCeleryPolling();
      mutate();
    },
  },
  watch: {
    "$root.frequentCeleryPolling": function (newValue) {
      // Watch for deactivation of frequent polling and refetch data check results

      if (!newValue) {
        this.$apollo.queries.dataCheckResults.refetch();
      }
    },
  },
};
</script>
