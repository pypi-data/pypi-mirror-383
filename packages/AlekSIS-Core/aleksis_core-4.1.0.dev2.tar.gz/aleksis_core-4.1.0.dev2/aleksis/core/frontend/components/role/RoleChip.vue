<script>
export default {
  name: "RoleChip",
  extends: "v-chip",
  props: {
    role: {
      type: Object,
      required: true,
    },
    /**
     * How to format the role-name inside the chip
     * short, long or both
     */
    format: {
      type: String,
      required: false,
      default: "long",
    },
  },
  computed: {
    name() {
      switch (this.format) {
        case "long":
          return this.role.name;
        case "short":
          return this.role.shortName;
        case "both":
          return `${this.role.shortName} (${this.role.name})`;
        default:
          return this.role.name;
      }
    },
  },
};
</script>

<template>
  <v-chip
    v-bind="$attrs"
    :color="role.bgColor"
    :style="{ color: role.fgColor }"
  >
    {{ name }}
  </v-chip>
</template>
