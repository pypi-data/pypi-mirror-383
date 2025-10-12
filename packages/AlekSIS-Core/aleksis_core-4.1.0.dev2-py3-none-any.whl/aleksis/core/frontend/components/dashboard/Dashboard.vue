<script setup>
import SecondaryActionButton from "../generic/buttons/SecondaryActionButton.vue";
import { buildQuery } from "./dashboardQuery";
import WidgetWrapper from "./WidgetWrapper.vue";
import { collections } from "aleksisAppImporter";
import { usePermissionStore } from "../../stores/permissionStore";
import { useQuery } from "../../composables/app/apollo";
import { computed, ref } from "vue";

const permissionStore = usePermissionStore();

permissionStore.addPermissions(["core.edit_dashboard_rule"]);

const isDefaultDashboard = ref(false);

const canEdit = computed(() => {
  return permissionStore.checkPermission("core.edit_dashboard_rule");
});

const widgetInfoMap = computed(() => {
  return collections.coreDashboardWidgets.items.reduce((map, widget) => {
    map[widget.typename] = widget;
    return map;
  }, {});
});

const { result: widgetsResult, onResult: onWidgets } = useQuery(buildQuery);

onWidgets((result) => {
  isDefaultDashboard.value = !result.data?.dashboard.hasOwn || false;
});
</script>

<template>
  <v-sheet>
    <div v-if="canEdit" class="d-flex justify-end mb-2">
      <secondary-action-button
        i18n-key="dashboard.edit"
        icon-text="$edit"
        :to="{ name: 'dashboard', query: { _ui_action: 'edit' } }"
      />
    </div>

    <div :class="{ dashboard: true, 'd-grid': !$vuetify.display.mobile }">
      <WidgetWrapper
        v-for="instance in widgetsResult?.dashboard?.my ?? []"
        :key="instance.id"
        v-bind="instance"
      >
        <component
          :is="widgetInfoMap[instance.widget.__typename].component"
          v-bind="{ widget: instance.widget, context: instance.context }"
          class="widget"
        />
      </WidgetWrapper>
    </div>

    <div
      v-if="canEdit && isDefaultDashboard"
      class="justify-end px-0 pt-1 auto-height text-subtitle-2"
    >
      {{ $t("dashboard.customizing_notice") }}
    </div>
  </v-sheet>
</template>

<style scoped>
.auto-height {
  height: auto;
}

.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1em;
}

.d-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-auto-rows: 1fr;
}

.widget {
  width: 100%;
  height: 100%;
}
</style>
