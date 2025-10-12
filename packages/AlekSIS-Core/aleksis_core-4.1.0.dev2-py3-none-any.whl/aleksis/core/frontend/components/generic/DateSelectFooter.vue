<script setup>
import DateField from "./forms/DateField.vue";

const modelValue = defineModel({ type: Object });

defineProps({
  loading: {
    type: Boolean,
    required: false,
    default: false,
  },
});

defineEmits(["input", "prev", "next"]);
</script>

<template>
  <v-footer app inset class="date-select-footer">
    <div class="d-flex align-center justify-center full-width">
      <icon-button
        large
        class="me-4"
        @click="$emit('prev')"
        icon-text="$prev"
        i18n-key="actions.scroll_prev"
      />
      <div class="flex-grow-0">
        <date-field
          variant="plain"
          hide-details
          v-model="modelValue"
          :label="$t('date_select.label')"
          :disabled="loading"
          readonly
        />
      </div>
      <icon-button
        large
        class="ms-4"
        @click="$emit('next')"
        icon-text="$next"
        i18n-key="actions.scroll_next"
      />
    </div>
  </v-footer>
</template>

<style scoped>
.auto-margin {
  margin: auto;
}
.date-select-footer {
  z-index: 5;
}
</style>
