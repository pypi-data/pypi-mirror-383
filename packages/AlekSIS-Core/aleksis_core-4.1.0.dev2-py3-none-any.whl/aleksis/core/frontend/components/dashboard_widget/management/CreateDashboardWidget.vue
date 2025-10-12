<script>
import { widgetTypes } from "./availableWidgets.graphql";
import ButtonMenu from "../../generic/ButtonMenu.vue";

export default {
  name: "CreateDashboardWidget",
  components: { ButtonMenu },
  props: {
    widgetInfoMap: {
      type: Object,
      default: () => ({}),
      required: false,
    },
  },
  emits: ["create"],
  data() {
    return {
      widgetTypes: [],
    };
  },
  methods: {
    create(type) {
      this.$emit("create", type);
    },
  },
  apollo: {
    widgetTypes: {
      query: widgetTypes,
      update: (data) => data.dashboard.widgetTypes,
    },
  },
};
</script>

<template>
  <button-menu
    text-translation-key="actions.create_widget"
    icon="$plus"
    variant="text"
    color="primary"
  >
    <v-list-item
      v-for="type in widgetTypes"
      :key="type.typeName"
      @click="create(type.modelName)"
    >
      <v-list-item-title>
        {{ $t(widgetInfoMap[type.typeName]?.nameKey || type.modelName) }}
      </v-list-item-title>
    </v-list-item>
  </button-menu>
</template>
