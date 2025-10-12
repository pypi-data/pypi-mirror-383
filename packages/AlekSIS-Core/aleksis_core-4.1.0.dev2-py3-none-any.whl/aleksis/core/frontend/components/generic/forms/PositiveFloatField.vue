<script setup>
import TextField from "./TextField.vue";
</script>

<template>
  <text-field
    v-bind="$attrs"
    :rules="$rules().isANumber.isGreaterThan(0).build(rules)"
    inputmode="decimal"
    :input-handler="inputHandler"
  >
    <template #append>
      <slot name="append" />
    </template>
  </text-field>
</template>

<script>
import formRulesMixin from "../../../mixins/formRulesMixin";

export default {
  name: "PositiveFloatField",
  extends: "TextField",
  mixins: [formRulesMixin],
  props: {
    rules: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  methods: {
    inputHandler(name) {
      return (event) => {
        if (event == null || !(typeof event === "string")) {
          this.$emit(name, event);
          return;
        }

        const num = this.$parseNumber(event);

        if (isNaN(num)) {
          this.$emit(name, null);
          return;
        }

        this.$emit(name, num);
      };
    },
  },
};
</script>
