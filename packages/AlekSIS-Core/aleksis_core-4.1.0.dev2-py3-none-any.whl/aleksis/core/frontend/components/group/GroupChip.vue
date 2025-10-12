<script>
export default {
  name: "GroupChip",
  extends: "v-chip",
  props: {
    group: {
      type: Object,
      required: true,
    },
    /**
     * How to format the group-name inside the chip
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
          return this.group.name;
        case "short":
          return this.group.shortName;
        case "both":
          return `${this.group.shortName} (${this.group.name})`;
        default:
          return this.group.name;
      }
    },
  },
};
</script>

<template>
  <v-chip
    v-bind="$attrs"
    :to="{ name: 'core.group', params: { id: group.id } }"
  >
    {{ name }}
  </v-chip>
</template>
