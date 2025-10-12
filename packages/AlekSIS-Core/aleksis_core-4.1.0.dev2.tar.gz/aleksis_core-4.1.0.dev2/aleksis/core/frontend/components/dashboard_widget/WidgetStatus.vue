<template>
  <v-chip variant="outlined" :color="color">
    <v-avatar start>
      <v-progress-circular
        indeterminate
        :size="16"
        :width="2"
        v-if="loading"
        :color="color"
      />
      <v-icon v-else :color="color">
        {{ icon }}
      </v-icon>
    </v-avatar>
    {{ $t(text) }}
  </v-chip>
</template>
<script>
import status, { OFF, ON, BROKEN, READY } from "./status";

export default {
  name: "WidgetStatus",
  props: {
    status: {
      type: String,
      default: OFF,
      validator: (value) => status.includes(value),
    },
    loading: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  computed: {
    color() {
      return {
        [OFF]: "",
        [ON]: "success",
        [READY]: "primary",
        [BROKEN]: "error",
      }[this.status];
    },
    icon() {
      return {
        [OFF]: "$dashboardWidgetOff",
        [ON]: "$dashboardWidgetOn",
        [READY]: "$dashboardWidgetReady",
        [BROKEN]: "$dashboardWidgetBroken",
      }[this.status];
    },
    text() {
      return {
        [OFF]: "dashboard.dashboard_widget.status.OFF",
        [ON]: "dashboard.dashboard_widget.status.ON",
        [READY]: "dashboard.dashboard_widget.status.READY",
        [BROKEN]: "dashboard.dashboard_widget.status.BROKEN",
      }[this.status];
    },
  },
};
</script>
