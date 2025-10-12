<script>
import { buildQuery } from "../dashboardQuery";
import { buildQuery as queryAvailable } from "../../dashboard_widget/management/dashboardWidgetQuerying";
import { collections } from "aleksisAppImporter";
import { ON } from "../../dashboard_widget/status";

import {
  deleteDashboardWidgetInstances,
  reorderDashboardWidgets,
} from "./manageDashboard.graphql";
import loadingMixin from "../../../mixins/loadingMixin";
import MovableWidget from "./MovableWidget.vue";
import Mascot from "../../generic/mascot/Mascot.vue";

export default {
  name: "ManageDashboard",
  components: {
    Mascot,
    MovableWidget,
  },
  mixins: [loadingMixin],
  props: {
    defaultDashboard: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  data() {
    return {
      hasOwn: false,
      dashboardWidgets: [],
      qAvailableWidgets: [],
      selectedWidgetId: undefined,
      deleteDashboardWidgetInstances,
    };
  },
  computed: {
    widgetInfoMap() {
      return collections.coreDashboardWidgets.items.reduce((map, widget) => {
        map[widget.typename] = widget;
        return map;
      }, {});
    },
    gridItems() {
      if (!this.hasOwn) {
        return [];
      }

      return this.dashboardWidgets.map((instance) => ({
        key: instance.id,
        x: instance.x + 1,
        y: instance.y + 1,
        w: instance.width,
        h: instance.height,
        data: instance,
      }));
    },
    availableWidgets() {
      return this.qAvailableWidgets.map((widget) => ({
        key: widget.id,
        x: "0",
        y: "0",
        w: 3,
        h: 1,
        data: widget,
      }));
    },
    gridLoading() {
      return (
        this.$apollo.queries.dashboardWidgets.loading ||
        this.$apollo.queries.qAvailableWidgets.loading
      );
    },
    backlink() {
      return this.defaultDashboard
        ? { name: "core.editDefaultDashboard" }
        : { name: "dashboard", query: { _ui_action: "default" } };
    },
  },
  apollo: {
    dashboardWidgets: {
      query: buildQuery,
      variables() {
        return {
          forceDefault: this.defaultDashboard,
        };
      },
      update: (data) => data.dashboard.my,
      result({ data }) {
        this.hasOwn = data.dashboard.hasOwn;
      },
    },
    qAvailableWidgets: {
      query: queryAvailable,
      update: (data) => data.dashboard.widgets,
      variables: () => ({ status: ON }),
    },
  },
  methods: {
    itemMovedToDashboard(eventData) {
      const widgetId =
        eventData.originGridId === "availableWidgets"
          ? eventData.data.id
          : eventData.data.widget.id;
      const id =
        eventData.originGridId === "availableWidgets"
          ? undefined
          : eventData.data.id;
      this.$apollo
        .mutate({
          mutation: reorderDashboardWidgets,
          variables: {
            widgetData: [
              {
                x: eventData.x - 1,
                y: eventData.y - 1,
                width: eventData.w,
                height: eventData.h,
                widget: widgetId,
                id,
              },
            ],
            isDefaultDashboard: this.defaultDashboard,
          },
          update: (store, data) => {
            // Current implemented for create | patch
            data = data.data.reorderDashboardWidgets;
            const { created, updated } = data;

            let query = {
              ...this.$apollo.queries.dashboardWidgets.options,
              variables: JSON.parse(
                this.$apollo.queries.dashboardWidgets.previousVariablesJson,
              ),
            };

            // Read the data from cache for query
            const cachedQuery = store.readQuery(query);
            if (cachedQuery) {
              // Update the store

              const idsToReplace = new Set(updated.map((obj) => obj.id));

              cachedQuery.dashboard.my.splice(
                0,
                cachedQuery.dashboard.my.length,
                ...cachedQuery.dashboard.my.filter(
                  (obj) => !idsToReplace.has(obj.id),
                ),
              );

              cachedQuery.dashboard.my.push(...updated);
              cachedQuery.dashboard.my.push(...created);

              this.selectedWidgetId = [...updated, ...created][0].id;

              // Write data back to the cache
              store.writeQuery({ ...query, data: cachedQuery });
            }
          },
        })
        .catch((error) => {
          this.handleMutationError(error);
        })
        .finally(() => {
          this.handleLoading(false);
        });
    },
    handleContainerDragStart(eventData) {
      this.selectedWidgetId = eventData.data.id;
    },
  },
};
</script>

<template>
  <div>
    <v-row>
      <v-col cols="12" lg="8" xl="9">
        <message-box type="info">
          {{
            $t(
              defaultDashboard
                ? "dashboard.manage_default_dashboard_hint"
                : "dashboard.manage_dashboard_hint",
            )
          }}
        </message-box>
      </v-col>

      <v-col
        cols="12"
        lg="4"
        xl="3"
        class="d-flex justify-space-between flex-wrap align-center"
      >
        <secondary-action-button
          i18n-key="actions.back_to_start"
          block
          :to="backlink"
          :active="false"
          :value="false"
          :input-value="false"
        />
      </v-col>

      <v-col cols="12" lg="8" xl="9" class="align-self-start" id="grid">
        <div id="align-grid" class="pb-4">
          <v-card v-for="index in 12" :key="index">
            <!-- eslint-disable-next-line vue/no-v-text-v-html-on-component -->
            <v-card-text v-text="index" class="text-center" />
          </v-card>
        </div>
        <drag-grid
          :cols="12"
          :rows="12"
          :model-value="gridItems"
          :loading="gridLoading"
          context="dashboard"
          @item-changed="itemMovedToDashboard"
          @container-drag-start="handleContainerDragStart"
          grid-id="dashboardGrid"
          id="dashboard"
          ref="dashboard"
        >
          <template #item="item">
            <movable-widget
              :widget="item"
              :selected="selectedWidgetId === item.data.id"
              :component="widgetInfoMap[item.data.widget.__typename].preview"
              @toggle="selectedWidgetId = item.data.id"
              @delete="deleteWidget(item.data.id)"
              :affected-query="$apollo.queries.dashboardWidgets"
              :gql-delete-mutation="deleteDashboardWidgetInstances"
              gql-data-key="dashboard.my"
              :position-allowed="$refs.dashboard.positionAllowed"
              @reposition="itemMovedToDashboard"
            />
          </template>
          <template #loader>
            <v-skeleton-loader type="sentences" />
          </template>
          <template #highlight>
            <v-skeleton-loader
              type="image"
              boilerplate
              height="100%"
              id="highlight"
            />
          </template>
          <v-card
            border
            v-if="!gridLoading && gridItems.length === 0"
            style="grid-column: 5/8; grid-row: 1"
          >
            <mascot type="ready_for_items" />
          </v-card>
        </drag-grid>
      </v-col>

      <v-col cols="12" lg="4" xl="3">
        <v-card>
          <v-card-text>
            <drag-grid
              :cols="6"
              :rows="12"
              :model-value="availableWidgets"
              :loading="$apollo.queries.qAvailableWidgets.loading"
              no-highlight
              context="dashboard"
              grid-id="availableWidgets"
            >
              <template #item="item">
                <component
                  :is="widgetInfoMap[item.data.__typename].preview"
                  :widget="item.data"
                  class="fullsize"
                />
              </template>
              <template #loader>
                <v-skeleton-loader type="image" />
              </template>
            </drag-grid>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<style>
#highlight > .v-skeleton-loader__image {
  height: 100%;
}
#align-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 1em;
}
</style>
