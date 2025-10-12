<script>
export default {
  name: "CollapseTriggerButton",
  props: {
    modelValue: {
      type: Boolean,
      default: false,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
    labelActive: {
      type: String,
      required: false,
      default: undefined,
    },
    icon: {
      type: String,
      required: false,
      default: "$expand",
    },
  },
  computed: {
    text() {
      return this.$t(
        this.modelValue && this.labelActive ? this.labelActive : this.label,
      );
    },
  },
  emits: ["update:modelValue"],
  methods: {
    handleClick() {
      this.$emit("update:modelValue", !this.modelValue);
    },
  },
};
</script>

<template>
  <v-btn
    v-bind="$attrs"
    variant="flat"
    @click="handleClick"
    id="collapseTriggerButton"
  >
    <span class="text-truncate inline-block">
      {{ text }}
    </span>
    <v-icon v-if="icon" :class="{ icon: true, rotated: modelValue }">{{
      icon
    }}</v-icon>
  </v-btn>
</template>

<style scoped>
.icon {
  transition: transform 0.3s;
}

.rotated {
  transform: rotate(-180deg);
}

.inline-block {
  display: inline-block;
}
</style>

<style>
#collapseTriggerButton > span.v-btn__content {
  width: 100%;
}
</style>
