<script>
import managementMixin from "../managementMixin";
import { updateStaticContentWidgets } from "../../management/dashboardWidgetManagement.graphql";

export default {
  name: "Management",
  mixins: [managementMixin],
  data() {
    return {
      internalContent: "",
    };
  },
  mounted() {
    this.internalContent = this.widget.content;
  },
  methods: {
    updateStatus(content) {
      this.mutate(
        updateStaticContentWidgets,
        {
          input: [
            {
              id: this.widget.id,
              content,
            },
          ],
        },
        (cached, incoming) => {
          incoming.forEach((widget) => {
            const index = cached.findIndex((c) => c.id === widget.id);
            cached[index].status = widget.status;
            cached[index].title = widget.title;
            cached[index].content = widget.content;
          });
          return cached;
        },
      );
    },
  },
};
</script>

<template>
  <v-row>
    <v-col cols="12" md="6">
      <v-card :elevation="0">
        <v-card-text class="pb-0">
          <v-textarea
            variant="outlined"
            v-model="internalContent"
            auto-grow
            :hint="
              $t(
                'dashboard.dashboard_widgets.static_content.fields.content_hint',
              )
            "
            :label="
              $t('dashboard.dashboard_widgets.static_content.fields.content')
            "
            persistent-hint
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <save-button
            :loading="loading"
            @click="updateStatus(internalContent)"
          />
        </v-card-actions>
      </v-card>
    </v-col>
    <v-col cols="12" md="6">
      <v-card :elevation="0">
        <v-card-title>
          {{ $t("dashboard.dashboard_widgets.static_content.fields.preview") }}
        </v-card-title>
        <!-- eslint-disable-next-line vue/no-v-text-v-html-on-component -->
        <v-card-text v-html="internalContent" />
      </v-card>
    </v-col>
  </v-row>
</template>
