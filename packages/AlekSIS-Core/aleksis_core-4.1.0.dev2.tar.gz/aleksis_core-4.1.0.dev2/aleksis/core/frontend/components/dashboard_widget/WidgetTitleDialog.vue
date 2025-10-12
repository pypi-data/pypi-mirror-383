<script>
import mutateMixin from "../../mixins/mutateMixin";
import { updateDashboardWidgets } from "./management/dashboardWidgetManagement.graphql";

export default {
  name: "WidgetTitleDialog",
  mixins: [mutateMixin],
  emits: ["update"],
  props: {
    widget: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      innerValue: "",
      menu: false,
    };
  },
  mounted() {
    this.innerValue = this.widget.title;
  },
  methods: {
    cancel() {
      this.innerValue = this.widget.title;
      this.menu = false;
    },
    save() {
      this.mutate(
        updateDashboardWidgets,
        {
          input: [
            {
              id: this.widget.id,
              title: this.innerValue,
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
  watch: {
    loading(newValue, oldValue) {
      if (!newValue && oldValue) {
        // We were loading but we aren't anymore → request finished, close dialog
        this.menu = false;
      }
    },
  },
};
</script>

<template>
  <span class="db-widget-dialog">
    <v-menu v-model="menu" :close-on-content-click="false" location="end">
      <template #activator="{ props }">
        <span class="mr-1 d-flex align-center">
          {{ widget.title }}

          <icon-button
            v-bind="props"
            icon-text="$edit"
            i18n-key="actions.edit"
            size="small"
          />
        </span>
      </template>

      <v-confirm-edit
        v-slot="{ model: proxyModel, actions }"
        v-model="innerValue"
        @cancel="cancel"
        @save="save"
      >
        <v-card
          class="mx-auto"
          min-width="300"
          rounded="lg"
          :title="$t('actions.edit_title')"
        >
          <template #text>
            <div aria-required="true">
              <v-text-field
                v-model="proxyModel.value"
                :label="$t('dashboard.dashboard_widget.widget_title')"
                single-line
                variant="outlined"
              />
            </div>
          </template>

          <template #actions>
            <v-spacer />
            <component :is="actions" />
          </template>
        </v-card>
      </v-confirm-edit>
    </v-menu>
  </span>
</template>

<style>
.db-widget-dialog .v-small-dialog__activator,
.db-widget-dialog .v-menu {
  display: inline;
}
</style>
