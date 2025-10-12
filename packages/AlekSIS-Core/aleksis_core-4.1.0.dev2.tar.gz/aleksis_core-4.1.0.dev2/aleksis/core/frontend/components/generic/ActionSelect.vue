<script setup>
import { minActionsProps } from "../../composables/useAction.js";

const props = defineProps({
  ...minActionsProps,
  /**
   * Disable activating the action
   * This hides the button that triggers the action
   */
  disabled: {
    type: Boolean,
    required: false,
    default: false,
  },
});

const emit = defineEmits(["performAction"]);

const selectedAction = defineModel("selectedAction", { type: String });
</script>

<template>
  <v-autocomplete
    clearable
    :items="actions"
    v-model="selectedAction"
    return-object
    :label="$t('actions.select_action')"
    item-title="name"
    variant="outlined"
    density="compact"
    :hint="$t('selection.num_items_selected', selectionCount)"
    persistent-hint
    :append-icon="disabled || !selectedAction ? '' : '$send'"
    @click:append="emit('performAction', selectedAction)"
  >
    <template #item="{ item, props }">
      <v-list-item density="compact" v-bind="props">
        <template #prepend v-if="item.icon">
          <v-icon>{{ item.icon }}</v-icon>
        </template>

        <v-list-item-title>{{ item.name }}</v-list-item-title>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>
