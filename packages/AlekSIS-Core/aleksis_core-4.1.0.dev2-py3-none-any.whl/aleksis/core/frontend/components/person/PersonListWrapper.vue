<template>
  <component :is="currentComponent" v-bind="componentProps" />
</template>

<script>
import PersonForm from "./PersonForm.vue";
import PersonList from "./PersonList.vue";

export default {
  computed: {
    currentComponent() {
      return this.$route.query._ui_action === "create"
        ? PersonForm
        : PersonList;
    },
    componentProps() {
      return this.$route.query._ui_action === "create"
        ? {
            fallbackUrl: { name: "core.persons" },
            isCreate: true,
          }
        : {};
    },
  },
};
</script>
