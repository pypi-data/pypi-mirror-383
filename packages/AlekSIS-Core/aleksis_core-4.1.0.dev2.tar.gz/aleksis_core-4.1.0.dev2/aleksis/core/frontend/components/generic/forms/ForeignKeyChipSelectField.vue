<script setup>
import ForeignKeyField from "./ForeignKeyField.vue";
</script>

<template>
  <foreign-key-field
    v-bind="{ ...$props, ...$attrs }"
    rounded
    hide-details
    filled
    :height="height"
    class="chip-select-field"
  >
    <template #prepend-inner>
      <slot name="prepend-inner" />
    </template>
    <template #item="data">
      <slot name="item" v-bind="data" />
    </template>
    <template #selection="data">
      <slot name="selection" v-bind="data" />
    </template>
    <template #createComponent="{ attrs, on, createMode }">
      <slot
        name="selection"
        v-bind="{ ...attrs, createMode: createMode }"
        v-on="on"
      ></slot>
    </template>
  </foreign-key-field>
</template>

<script>
import chipHeightMixin from "../../../mixins/chipHeightMixin";

export default {
  name: "ForeignKeyChipSelectField",
  extends: ForeignKeyField,
  mixins: [chipHeightMixin],
};
</script>

<style lang="scss">
.chip-select-field {
  & .v-input__control > .v-input__slot {
    min-height: auto !important;
    padding: 0 12px;
    cursor: pointer !important;
  }
  & .v-input__slot > .v-progress-linear {
    margin-left: v-bind(progressPadding);
    width: calc(100% - v-bind(heightString));
    top: calc(100% - 2px);
  }
  & .v-input__slot > .v-select__slot {
    & input {
      color: v-bind(color);
    }
    & > .v-input__append-inner {
      margin-top: 0;
      align-self: center !important;

      & i {
        color: v-bind(color);
      }
    }
  }
  & .v-input__append-outer {
    margin-top: 0;
    margin-bottom: 0;
    align-self: center !important;
  }
}
</style>
