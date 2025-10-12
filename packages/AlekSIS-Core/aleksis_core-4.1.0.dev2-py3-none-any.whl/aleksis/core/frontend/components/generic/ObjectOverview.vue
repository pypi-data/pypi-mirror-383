<template>
  <div>
    <slot name="loading" v-if="$apollo.queries.object.loading"></slot>
    <slot v-else-if="object" v-bind="object"></slot>
    <error-page
      v-else
      :short-error-message-key="shortErrorMessageKey"
      :long-error-message-key="longErrorMessageKey"
      :redirect-button-text-key="redirectButtonTextKey"
      :redirect-route-name="redirectRouteName"
      :redirect-button-icon="redirectButtonIcon"
    />
  </div>
</template>

<script>
import { useAppStore } from "../../stores/appStore";

export default {
  setup() {
    const appStore = useAppStore();
    return { appStore };
  },
  name: "ObjectOverview",
  props: {
    titleAttr: {
      type: String,
      required: true,
    },
    query: {
      type: Object,
      required: true,
    },
    id: {
      type: String,
      required: false,
      default: undefined,
    },
    shortErrorMessageKey: {
      type: String,
      required: false,
      default: "network_errors.error_404",
    },
    longErrorMessageKey: {
      type: String,
      required: false,
      default: "network_errors.page_not_found",
    },
    redirectButtonTextKey: {
      type: String,
      required: false,
      default: "network_errors.back_to_start",
    },
    redirectRouteName: {
      type: String,
      required: false,
      default: "dashboard",
    },
    redirectButtonIcon: {
      type: String,
      required: false,
      default: "$home",
    },
  },
  data() {
    return {
      object: undefined,
    };
  },
  methods: {
    getTitleAttr(obj) {
      let tmpObj = obj;
      this.titleAttr.split(".").forEach((attr) => {
        tmpObj = tmpObj[attr];
      });
      return tmpObj;
    },
  },
  apollo: {
    object() {
      const that = this;
      return {
        query: this.query,
        variables() {
          if (this.id !== undefined) {
            return {
              id: this.id,
            };
          }
          return {};
        },
        result({ data }) {
          if (data && data.object) {
            that.appStore.setPageTitle(that.getTitleAttr(data.object));
          }
        },
      };
    },
  },
};
</script>

<style scoped></style>
