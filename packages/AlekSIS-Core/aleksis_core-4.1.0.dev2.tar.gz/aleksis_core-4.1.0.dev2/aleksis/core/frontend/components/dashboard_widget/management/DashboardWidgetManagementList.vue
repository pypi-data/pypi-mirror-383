<template>
  <c-r-u-d-provider
    :i18n-key="i18nKey"
    :query="gqlQuery"
    :data-key="gqlDataKey"
    :elevated="false"
    :object-schema="{ type: 'DashboardWidgetType' }"
    disable-create
    :create-mutation="createMutation"
    :create-options="{ dataKey: 'items' }"
    :delete-mutation="deleteDashboardWidgets"
  >
    <!-- TODO ↑ wrong objectschema, how to ? -->
    <template #additionalActions="{ create }">
      <create-dashboard-widget
        @create="create({ widgetTypes: [$event] })"
        :widget-info-map="widgetInfoMap"
      />
      <secondary-action-button
        icon-text="mdi-view-dashboard-edit-outline"
        i18n-key="dashboard.manage_default_dashboard"
        :to="{ name: 'core.editDefaultDashboard' }"
      />
    </template>
    <template #view="view">
      <v-expansion-panels>
        <dashboard-widget-wrapper
          v-for="item in view.queryItems"
          :key="item.id"
          :widget-data="item"
          :widget-info="widgetInfoMap[item.__typename]"
          class="mb-2"
          :affected-query="lastQuery"
          :delete-fn="view.delete"
          :delete-loading="view.deleteLoading"
          gql-data-key="dashboard.widgets"
        />
      </v-expansion-panels>
    </template>
  </c-r-u-d-provider>
</template>

<script setup>
import { buildQuery, buildCreateMutation } from "./dashboardWidgetQuerying";
import { collections } from "aleksisAppImporter";
import {
  deleteDashboardWidgets,
  updateDashboardWidgets,
} from "./dashboardWidgetManagement.graphql";

import CRUDProvider from "../../generic/crud/CRUDProvider.vue";
import DashboardWidgetWrapper from "../ManageDashboardWidgetWrapper.vue";
import CreateDashboardWidget from "./CreateDashboardWidget.vue";

import { ref, reactive, computed } from "vue";
import { useI18n } from "../../../composables/app/useI18n";

const { t } = useI18n();

const headers = reactive([
  {
    text: t("dashboard_widget.name"),
    value: "title",
  },
  {
    text: t("dashboard_widget.status"),
    value: "status",
  },
]);

const selected = ref([]);
const i18nKey = "dashboard_widget";

const gqlQuery = ref(buildQuery());
const gqlDataKey = "dashboard.widgets";

const defaultItem = ref({
  title: "",
  status: "OFF",
});

const lastQuery = ref(null);

const widgetInfoMap = computed(() => {
  return collections.coreDashboardWidgets.items.reduce((map, widget) => {
    map[widget.typename] = widget;
    return map;
  }, {});
});

const createMutation = ref(buildCreateMutation());
</script>
