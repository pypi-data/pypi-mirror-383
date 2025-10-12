<script>
import WidgetStatus from "./WidgetStatus.vue";
import ButtonMenu from "../generic/ButtonMenu.vue";
import MarkWidgetDialog from "./MarkWidgetDialog.vue";
import mutatePropsMixin from "../../mixins/mutatePropsMixin";
import WidgetTitleDialog from "./WidgetTitleDialog.vue";

export default {
  name: "DashboardWidgetWrapper",
  components: { WidgetTitleDialog, ButtonMenu, MarkWidgetDialog, WidgetStatus },
  mixins: [mutatePropsMixin],
  props: {
    mode: {
      type: String,
      default: "widget",
    },
    widgetData: {
      type: Object,
      required: true,
    },
    widgetInfo: {
      type: Object,
      required: true,
    },
    deleteFn: {
      type: Function,
      required: true,
    },
    deleteLoading: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      loading: false,
    };
  },
};
</script>

<template>
  <v-expansion-panel>
    <v-expansion-panel-title class="d-flex align-center">
      <div class="d-flex align-center">
        <widget-title-dialog
          :widget="widgetData"
          v-bind="mutateProps"
          gql-data-key="dashboard.widgets"
        />
        <v-chip label variant="outlined" size="small">
          {{ $t(widgetInfo.shortNameKey) }}
        </v-chip>
      </div>
      <v-spacer />
      <widget-status :status="widgetData.status" :loading="loading" />
      <mark-widget-dialog
        :status="widgetData.status"
        :widget="widgetData"
        v-bind="mutateProps"
        gql-data-key="dashboard.widgets"
        :delete-fn="deleteFn"
        :delete-loading="deleteLoading"
        @loading="loading = $event"
      />
    </v-expansion-panel-title>
    <v-expansion-panel-text>
      <component
        :is="widgetInfo.management"
        :widget="widgetData"
        v-bind="mutateProps"
      />
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>
