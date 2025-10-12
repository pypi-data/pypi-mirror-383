<script>
export default {
  name: "WidgetWrapper",
  props: {
    x: {
      type: Number,
      required: true,
    },
    y: {
      type: Number,
      required: true,
    },
    width: {
      type: Number,
      required: true,
    },
    height: {
      type: Number,
      required: true,
    },
  },
  computed: {
    column() {
      return `${this.x + 1} / span ${this.width}`;
    },
    row() {
      return `${this.y + 1} / span ${this.height}`;
    },
  },
};
</script>

<template>
  <div>
    <slot />
  </div>
</template>

<style scoped>
div {
  grid-column: v-bind(column);
  grid-row: v-bind(row);
}
</style>
