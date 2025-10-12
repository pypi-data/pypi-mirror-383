<template>
  <v-chip v-bind="$attrs">
    <v-avatar :start="!onlyShowCount" v-if="count !== null">
      {{ $n(count) }}
    </v-avatar>
    <slot v-if="!onlyShowCount" />
  </v-chip>
</template>

<script>
export default {
  name: "CounterChip",
  extends: "v-chip",
  props: {
    count: {
      type: [Number, null],
      required: false,
      default: null,
    },
    onlyShowCount: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
};
</script>
