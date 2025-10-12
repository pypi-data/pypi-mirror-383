<!-- TODO: This is broken now -> Int uses v-number-input directly for now -->
<script setup>
import TextField from "./TextField.vue";
</script>

<template>
  <text-field
    v-bind="$attrs"
    :rules="
      $rules()
        .isANumber.isAWholeNumber.isGreaterThan(0)
        .isSmallerThan(32767)
        .build(rules)
    "
    inputmode="numeric"
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
  name: "PositiveSmallIntegerField",
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

        this.$emit(name, Math.max(0, Math.min(num, 32767)));
      };
    },
  },
};
</script>
