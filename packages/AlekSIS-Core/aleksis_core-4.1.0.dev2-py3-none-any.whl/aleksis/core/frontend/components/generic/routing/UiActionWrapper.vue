<template>
  <component :is="currentComponent" v-bind="{ ...$attrs, ...componentProps }" />
</template>

<script>
export default {
  data() {
    return {
      components: {
        default: "v-sheet",
      },
      props: {
        default: {},
      },
    };
  },
  methods: {
    getProps(action) {
      if (action in this.props) {
        return this.props[action];
      }
      return this.props["default"];
    },
  },
  computed: {
    currentComponent() {
      if (this.$route.query._ui_action in this.components) {
        return this.components[this.$route.query._ui_action];
      }
      return this.components["default"];
    },
    componentProps() {
      return this.getProps(this.$route.query._ui_action);
    },
  },
};
</script>
