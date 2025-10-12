<script>
import managementMixin from "../managementMixin";
import { updateExternalLinkWidgets } from "../../management/dashboardWidgetManagement.graphql";

export default {
  name: "Management",
  mixins: [managementMixin],
  data() {
    return {
      internalUrl: "",
      internalIconUrl: "",
    };
  },
  mounted() {
    this.internalUrl = this.widget.url;
    this.internalIconUrl = this.widget.iconUrl;
  },
  methods: {
    updateStatus(url, iconUrl) {
      this.mutate(
        updateExternalLinkWidgets,
        {
          input: [
            {
              id: this.widget.id,
              url,
              iconUrl,
            },
          ],
        },
        (cached, incoming) => {
          incoming.forEach((widget) => {
            const index = cached.findIndex((c) => c.id === widget.id);
            cached[index].status = widget.status;
            cached[index].title = widget.title;
            cached[index].url = widget.url;
            cached[index].iconUrl = widget.iconUrl;
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
    <v-col cols="12">
      <v-card :elevation="0">
        <v-card-text class="pb-0">
          <v-text-field
            variant="outlined"
            v-model="internalUrl"
            :label="$t('dashboard.dashboard_widgets.external_link.fields.url')"
          />
          <v-text-field
            variant="outlined"
            v-model="internalIconUrl"
            :label="
              $t('dashboard.dashboard_widgets.external_link.fields.icon_url')
            "
          />
        </v-card-text>
        <v-card-actions>
          <save-button
            :loading="loading"
            @click="updateStatus(internalUrl, internalIconUrl)"
          />
        </v-card-actions>
      </v-card>
    </v-col>
  </v-row>
</template>
