<template>
  <secondary-action-button v-bind="$attrs" :i18n-key="i18nKey">
    <v-icon v-if="filterIcon" start>{{ filterIcon }}</v-icon>
    <span>{{ $t(i18nKey) }}</span>
    <v-badge
      v-if="activeFilterCount"
      color="secondary"
      :content="activeFilterCount"
      inline
      class="mr-2"
    >
    </v-badge>
    <icon-button
      @click.stop="emit('clear')"
      size="small"
      density="compact"
      v-if="activeFilterCount"
      icon-text="$clear"
      i18n-key="actions.clear_filters"
    />
  </secondary-action-button>
</template>

<script setup>
import { computed, defineProps } from "vue";
import { activeFilterCountProps } from "../../../composables/crud/useCRUDComponents";

const emit = defineEmits(["clear"]);
const props = defineProps({
  i18nKey: {
    type: String,
    required: false,
    default: "actions.filter",
  },
  ...activeFilterCountProps,
});

const filterIcon = computed(() =>
  props.activeFilterCount > 0 ? "$filterSet" : "$filterEmpty",
);
</script>
