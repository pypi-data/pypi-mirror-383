<!-- This is like a v-text-field with an extra inputHandler prop. -->
<!-- inputHandler receives the v-text-field's input and can transform it -->

<template>
  <v-text-field v-bind="$attrs" v-on="on">
    <template #append>
      <slot name="append" />
    </template>
  </v-text-field>
</template>

<script>
export default {
  name: "TextField",
  extends: "v-text-field",
  props: {
    inputHandler: {
      type: Function,
      required: false,
      default: (x) => x,
    },
  },
  computed: {
    on() {
      return {
        input: this.inputHandler("input"),
        change: this.inputHandler("change"),
        replace: this.inputHandler("replace"),
      };
    },
  },
};
</script>
