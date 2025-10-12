<template>
  <div class="d-flex">
    <v-btn
      v-if="step > 1"
      color="primary"
      variant="text"
      @click="$emit('set-step', step - 1)"
    >
      <v-icon start>mdi-chevron-left</v-icon>
      {{ $t("actions.back") }}
    </v-btn>
    <v-spacer />
    <v-btn
      v-if="finalStep"
      color="primary"
      :disabled="nextDisabled || nextLoading"
      :loading="nextLoading"
      @click="$emit('confirm')"
    >
      {{ $t("actions.confirm") }}
      <v-icon end>mdi-send-outline</v-icon>
    </v-btn>
    <v-btn
      v-else
      color="primary"
      :disabled="nextDisabled || nextLoading"
      :loading="nextLoading"
      @click="$emit('set-step', step + 1)"
    >
      {{ $t(nextI18nKey) }}
      <v-icon end>mdi-chevron-right</v-icon>
    </v-btn>
  </div>
</template>

<script>
export default {
  name: "ControlRow",
  props: {
    step: {
      type: Number,
      required: true,
    },
    nextDisabled: {
      type: Boolean,
      default: false,
    },
    finalStep: {
      type: Boolean,
      default: false,
    },
    nextLoading: {
      type: Boolean,
      default: false,
    },
    nextI18nKey: {
      type: String,
      default: "actions.next",
    },
  },
};
</script>
