<script>
import { defineComponent } from "vue";
import CancelButton from "../buttons/CancelButton.vue";
import PrimaryActionButton from "../buttons/PrimaryActionButton.vue";

export default defineComponent({
  name: "ConfirmDialog",
  components: { PrimaryActionButton, CancelButton },
  props: {
    value: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    confirm() {
      console.log("Confirming");
      this.$emit("confirm");
      this.$emit("input", false);
    },
    cancel() {
      console.log("Cancelling");
      this.$emit("cancel");
      this.$emit("input", false);
    },
  },
});
</script>

<template>
  <v-dialog :model-value="value" @click:outside="cancel" max-width="400">
    <v-card>
      <v-card-title>
        <slot name="title"></slot>
      </v-card-title>

      <v-card-text>
        <slot name="text"></slot>
      </v-card-text>

      <v-card-actions>
        <cancel-button @click="cancel">
          <slot name="cancel"></slot>
        </cancel-button>
        <v-spacer></v-spacer>
        <primary-action-button @click="confirm" i18n-key="actions.confirm">
          <slot name="confirm"></slot>
        </primary-action-button>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped></style>
