<script>
import ButtonMenu from "../generic/ButtonMenu.vue";
import status, { BROKEN, OFF, ON, READY } from "./status";
import DeleteDialog from "../generic/dialogs/DeleteDialog.vue";
import mutateMixin from "../../mixins/mutateMixin";
import {
  deleteDashboardWidgets,
  updateDashboardWidgets,
} from "./management/dashboardWidgetManagement.graphql";

export default {
  name: "MarkWidgetDialog",
  components: { ButtonMenu, DeleteDialog },
  mixins: [mutateMixin],
  emits: ["update"],
  props: {
    status: {
      type: String,
      default: OFF,
      validator: (value) => status.includes(value),
    },
    widget: {
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
      deleteDialog: false,
      deleteDashboardWidgets,
    };
  },
  computed: {
    choices() {
      let choices = [];

      // Users cannot turn OFF a widget (will be done automatically if it's not READY)
      // Users can turn a widget to READY if its currently ON or BROKEN
      // Users can turn a widget ON ony if its currently READY or BROKEN
      // Users cannot change a widget to BROKEN (will be done automatically, e.g. by datachecks)

      if (this.status === ON || this.status === BROKEN) {
        choices.push({
          code: READY,
          icon: "$dashboardWidgetReady",
          text: "dashboard.dashboard_widget.status.READY",
          color: "info",
        });
      }
      if (this.status === READY || this.status === BROKEN) {
        choices.push({
          code: ON,
          icon: "$dashboardWidgetOn",
          text: "dashboard.dashboard_widget.status.ON",
          color: "success",
        });
      }

      if (this.status === OFF) {
        choices.push({
          text: "dashboard.dashboard_widget.status.OFF_helper",
          disabled: true,
          icon: "$warning",
        });
      }

      return choices;
    },
  },
  methods: {
    updateStatus(status) {
      this.mutate(
        updateDashboardWidgets,
        {
          input: [
            {
              id: this.widget.id,
              status,
            },
          ],
        },
        (cached, incoming) => {
          incoming.forEach((widget) => {
            const index = cached.findIndex((c) => c.id === widget.id);
            cached[index].status = widget.status;
            cached[index].title = widget.title;
          });
          return cached;
        },
      );
    },
  },
};
</script>

<template>
  <div>
    <button-menu
      text-translation-key="actions.change_status"
      icon-only
      icon="mdi-dots-vertical"
      variant="icon"
    >
      <v-list-item>
        <v-list-subheader>
          {{ $t("actions.change_status") }}
        </v-list-subheader>
      </v-list-item>
      <v-list-item
        v-for="choice in choices"
        :key="choice.text"
        :class="choice.color + '--text'"
        :disabled="choice.disabled || !choice.code"
        @click="updateStatus(choice.code)"
      >
        <template #prepend>
          <v-icon :color="choice.color">{{ choice.icon }}</v-icon>
        </template>
        <v-list-item-title>
          {{ $t(choice.text) }}
        </v-list-item-title>
      </v-list-item>

      <v-list-item>
        <div class="text-subtitle-2">{{ $t("actions.more_actions") }}</div>
      </v-list-item>
      <v-list-item class="text-error" @click="deleteDialog = true">
        <template #prepend>
          <v-icon color="error">$deleteContent</v-icon>
        </template>
        <v-list-item-title>
          {{ $t("actions.delete") }}
        </v-list-item-title>
      </v-list-item>
    </button-menu>

    <DeleteDialog
      :key="widget.id"
      v-model:dialog-mode="deleteDialog"
      :loading="deleteLoading"
      :delete-items="[widget]"
      name-attribute="title"
      @delete="deleteFn({ ids: [widget.id] })"
    />
  </div>
</template>
