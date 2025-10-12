<script setup>
import { ref, onMounted } from "vue";

import { minActionsProps } from "../../../composables/useAction.js";
import {
  activeFilterCountProps,
  disableProps,
  CRUDBarProps,
} from "../../../composables/crud/useCRUDComponents.js";

import FilterButton from "../buttons/FilterButton.vue";
import ActionSelect from "../ActionSelect.vue";
import CreateButton from "../buttons/CreateButton.vue";

// Update notices:
// Use disabled instead of lock
const props = defineProps({
  ...minActionsProps,
  ...disableProps,
  ...CRUDBarProps,
  ...activeFilterCountProps,
  crud: {
    type: Object,
    required: true,
  },
});

const searchString = defineModel("searchString", { type: String });
const selectedAction = defineModel("selectedAction");

defineEmits(["promptFilters", "clearFilters", "performAction", "createMode"]);

const rootEl = ref();
const actualHeight = ref("0px");
onMounted(() => {
  actualHeight.value = `${rootEl.value.scrollHeight}px`;
});
</script>

<template>
  <v-toolbar
    ref="rootEl"
    class="height-fit child-height-fit"
    :flat="props.flat"
    :scroll-behavior="props.hideOnScroll ? 'hide' : undefined"
    :height="actualHeight"
  >
    <v-row class="flex-wrap gap align-baseline pa-2" no-gutters>
      <!-- @slot Insert title at beginning of header -->
      <slot name="title" />
      <div class="d-flex flex-wrap w-100 w-md-auto gap align-center">
        <filter-button
          v-if="!props.disableFilter"
          class="my-1 button-40"
          :disabled="props.disabled"
          :active-filter-count="props.activeFilterCount"
          @click="$emit('promptFilters')"
          @clear="$emit('clearFilters')"
        />
        <div class="my-1 w-100 w-md-auto" v-if="!props.disableSearch">
          <v-text-field
            v-model="searchString"
            type="search"
            clearable
            rounded
            hide-details
            single-line
            prepend-inner-icon="$search"
            density="compact"
            variant="outlined"
            :placeholder="$t('actions.search')"
            :disabled="props.disabled"
            min-width="16ch"
          />
        </div>
        <div
          class="my-1"
          v-if="!props.disableActions"
          v-show="props.actions.length > 0"
        >
          <action-select
            v-model:selected-action="selectedAction"
            @perform-action="$emit('performAction', $event)"
            :actions="props.actions"
            :selection-count="props.selectionCount"
            :disabled="props.disabled"
          />
        </div>
      </div>
      <v-spacer class="flex-grow-0 flex-sm-grow-1 mx-n1 mx-sm-0"></v-spacer>
      <create-button
        v-if="!props.disableCreate"
        color="secondary"
        @click="$emit('createMode')"
        :disabled="props.disabled"
      />
      <!-- @slot Insert additional things - actions/buttons - in the toolbar header -->
      <slot name="additionalActions" v-bind="props.crud" />
      <component
        :is="action.component"
        v-bind="action.props"
        v-for="action in props.additionalActions"
        :key="action.name"
      />
    </v-row>
  </v-toolbar>
</template>

<style>
.gap {
  gap: 0.5rem;
}
.height-fit,
.child-height-fit > * {
  height: fit-content !important;
}
.button-40 {
  min-height: 40px;
}
</style>
