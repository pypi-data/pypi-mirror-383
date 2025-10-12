<template>
  <v-tooltip location="bottom">
    <template #activator="{ props }">
      <v-btn
        location="right"
        icon
        v-bind="props"
        @click="handleClick"
        :loading="status === $options.UPDATING"
      >
        <v-icon v-if="status !== $options.UPDATING" :color="color">
          {{ icon }}
        </v-icon>
      </v-btn>
    </template>
    <span>{{ text }}</span>
  </v-tooltip>
</template>

<script>
export default {
  ERROR: "ERROR", // Something went wrong
  SAVED: "SAVED", // Everything alright
  UPDATING: "UPDATING", // We are sending something to the server
  CHANGES: "CHANGES", // the user changed something, but it has not been saved yet
  name: "UpdateIndicator",
  emits: ["manual-update"],
  props: {
    status: {
      type: String,
      required: true,
    },
  },
  computed: {
    text() {
      switch (this.status) {
        case this.$options.SAVED:
          return this.$t("status.saved");
        case this.$options.UPDATING:
          return this.$t("status.updating");
        case this.$options.CHANGES:
          return this.$t("status.changes");
        default:
          return this.$t("status.error");
      }
    },
    color() {
      switch (this.status) {
        case this.$options.SAVED:
          return "success";
        case this.$options.CHANGES:
          return "secondary";
        case this.$options.UPDATING:
          return "secondary";
        default:
          return "error";
      }
    },
    icon() {
      switch (this.status) {
        case this.$options.SAVED:
          return "$success";
        case this.$options.CHANGES:
          return "mdi-dots-horizontal";
        default:
          return "$warning";
      }
    },
    isAbleToClick() {
      return (
        this.status === this.$options.CHANGES ||
        this.status === this.$options.ERROR
      );
    },
  },
  methods: {
    handleClick() {
      if (this.isAbleToClick) {
        this.$emit("manual-update");
      }
    },
  },
};
</script>
