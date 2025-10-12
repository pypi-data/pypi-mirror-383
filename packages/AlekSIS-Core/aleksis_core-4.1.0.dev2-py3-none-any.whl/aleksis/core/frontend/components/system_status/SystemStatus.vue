<script setup>
import { reactive } from "vue";
import CopyToClipboardButton from "../generic/CopyToClipboardButton.vue";
import { setMaintenanceMode } from "./setMaintenanceMode.graphql";

const mutation = reactive(setMaintenanceMode);
</script>

<template>
  <div>
    <template v-if="$apollo.queries.systemProperties.loading">
      <v-skeleton-loader type="card,card,card"></v-skeleton-loader>
    </template>
    <template v-else>
      <v-card class="mb-4" :loading="$apollo.queries.systemProperties.loading">
        <v-card-title>
          {{ $t("administration.system_status.system_checks.title") }}
        </v-card-title>
        <v-list lines="two">
          <v-list-item>
            <template #prepend>
              <v-icon
                :color="
                  systemProperties.maintenanceMode ? 'warning' : 'success'
                "
              >
                {{ maintenanceModeIcon }}
              </v-icon>
            </template>

            <v-list-item-title>
              {{
                systemProperties.maintenanceMode
                  ? $t(
                      "administration.system_status.system_checks.maintenance_mode.enabled.title",
                    )
                  : $t(
                      "administration.system_status.system_checks.maintenance_mode.disabled.title",
                    )
              }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{
                systemProperties.maintenanceMode
                  ? $t(
                      "administration.system_status.system_checks.maintenance_mode.enabled.subtitle",
                    )
                  : $t(
                      "administration.system_status.system_checks.maintenance_mode.disabled.subtitle",
                    )
              }}
            </v-list-item-subtitle>

            <template #append>
              <v-list-item-action>
                <ApolloMutation
                  :mutation="mutation"
                  :variables="{ mode: !systemProperties.maintenanceMode }"
                  :refetch-queries="systemPropertiesQuery"
                >
                  <template #default="{ mutate, loading, error }">
                    <v-switch
                      inset
                      :loading="loading"
                      @click="mutate"
                      :model-value="systemProperties.maintenanceMode"
                    />
                  </template>
                </ApolloMutation>
              </v-list-item-action>
            </template>
          </v-list-item>
          <v-list-item>
            <template #prepend>
              <v-icon
                :color="systemProperties.debugMode ? 'warning' : 'success'"
              >
                {{ debugModeIcon }}
              </v-icon>
            </template>

            <v-list-item-title>
              {{
                systemProperties.debugMode
                  ? $t(
                      "administration.system_status.system_checks.debug_mode.enabled.title",
                    )
                  : $t(
                      "administration.system_status.system_checks.debug_mode.disabled.title",
                    )
              }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{
                systemProperties.debugMode
                  ? $t(
                      "administration.system_status.system_checks.debug_mode.enabled.subtitle",
                    )
                  : $t(
                      "administration.system_status.system_checks.debug_mode.disabled.subtitle",
                    )
              }}
            </v-list-item-subtitle>

            <template #append>
              <v-list-item-action>
                <v-switch
                  inset
                  disabled
                  :model-value="systemProperties.debugMode"
                />
              </v-list-item-action>
            </template>
          </v-list-item>
        </v-list>
      </v-card>

      <v-card class="mb-4">
        <v-card-title>
          {{ $t("administration.system_status.system_health.title") }}
        </v-card-title>
        <v-data-table
          :headers="healthCheckPluginHeaders"
          :items="healthCheckPlugins"
          :items-per-page="-1"
          hide-default-footer
          :loading="$apollo.queries.healthCheckPlugins.loading"
        >
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.status="{ item }">
            <v-tooltip location="bottom">
              <template #activator="{ props }">
                <v-icon
                  v-bind="props"
                  :color="item.status ? 'success' : 'error'"
                >
                  {{ getHealthCheckIcon(item.status) }}
                </v-icon>
              </template>
              <span>{{ item.prettyStatus }}</span>
            </v-tooltip>
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.timeTaken="{ item }">
            {{ item.timeTaken ? item.timeTaken : "–" }}
          </template>
        </v-data-table>
      </v-card>

      <v-card class="mb-4">
        <v-card-title>
          {{ $t("administration.system_status.celery_tasks.title") }}
        </v-card-title>
        <v-data-table
          :headers="celeryTaskHeaders"
          :items="celeryInspectTaskResults"
          :items-per-page="-1"
          hide-default-footer
          :loading="$apollo.queries.celeryInspectTaskResults.loading"
        >
          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.dateDone="{ item }">
            {{ $d($parseISODate(item.dateDone), "shortDateTime") }}
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.status="{ item }">
            <v-tooltip location="bottom">
              <template #activator="{ props }">
                <v-icon
                  v-bind="props"
                  :color="getCeleryStatusColor(item.status)"
                >
                  {{ getCeleryStatusIcon(item.status) }}
                </v-icon>
              </template>
              <span>{{ item.status }}</span>
            </v-tooltip>
          </template>

          <!-- eslint-disable-next-line vue/valid-v-slot -->
          <template #item.taskId="{ item }">
            <v-row align="center">
              <code>{{ item.taskId }}</code>
              <copy-to-clipboard-button :text="item.taskId" />
            </v-row>
          </template>
        </v-data-table>
      </v-card>
    </template>
  </div>
</template>

<script>
import {
  gqlSystemStatus,
  gqlHealthCheckPlugins,
  gqlCeleryInspectTaskResults,
} from "./systemStatus.graphql";

export default {
  name: "SystemStatus",
  apollo: {
    systemProperties: {
      query: gqlSystemStatus,
      fetchPolicy: "network-only",
    },
    healthCheckPlugins: {
      query: gqlHealthCheckPlugins,
      fetchPolicy: "network-only",
    },
    celeryInspectTaskResults: {
      query: gqlCeleryInspectTaskResults,
      fetchPolicy: "network-only",
    },
  },
  data() {
    return {
      healthCheckPluginHeaders: [
        {
          text: this.$t(
            "administration.system_status.system_health.headers.status",
          ),
          value: "status",
          width: "8em",
        },
        {
          text: this.$t(
            "administration.system_status.system_health.headers.identifier",
          ),
          value: "identifier",
        },
        {
          text: this.$t(
            "administration.system_status.system_health.headers.time_taken",
          ),
          value: "timeTaken",
        },
      ],
      celeryTaskHeaders: [
        {
          text: this.$t(
            "administration.system_status.celery_tasks.headers.status",
          ),
          value: "status",
          width: "8em",
        },
        {
          text: this.$t(
            "administration.system_status.celery_tasks.headers.task_name",
          ),
          value: "taskName",
        },
        {
          text: this.$t(
            "administration.system_status.celery_tasks.headers.task_id",
          ),
          value: "taskId",
        },
        {
          text: this.$t(
            "administration.system_status.celery_tasks.headers.date_done",
          ),
          value: "dateDone",
        },
      ],
      celeryTaskStatus: [
        {
          value: "PENDING",
          color: "warning",
          icon: "mdi-timer-sand-empty",
        },
        {
          value: "STARTED",
          color: "warning",
          icon: "mdi-timer-sand",
        },
        {
          value: "SUCCESS",
          color: "success",
          icon: "$success",
        },
        {
          value: "FAILURE",
          color: "error",
          icon: "$error",
        },
        {
          value: "RETRY",
          color: "warning",
          icon: "mdi-timer-sand-full",
        },
        {
          value: "REVOKED",
          color: "error",
          icon: "$cancel",
        },
      ],
      systemProperties: {},
      healthCheckPlugins: [],
      celeryInspectTaskResults: [],
    };
  },
  computed: {
    systemPropertiesQuery() {
      return () => [{ query: gqlSystemStatus }];
    },
    maintenanceModeIcon() {
      return this.systemProperties.maintenanceMode ? "$warning" : "$success";
    },
    debugModeIcon() {
      return this.systemProperties.debugMode ? "$warning" : "$success";
    },
  },
  methods: {
    getCeleryStatusColor(status) {
      return this.celeryTaskStatus.find((s) => s.value === status)?.color;
    },
    getCeleryStatusIcon(status) {
      return this.celeryTaskStatus.find((s) => s.value === status)?.icon;
    },
    getHealthCheckIcon(status) {
      return status ? "$success" : "$warning";
    },
  },
};
</script>
