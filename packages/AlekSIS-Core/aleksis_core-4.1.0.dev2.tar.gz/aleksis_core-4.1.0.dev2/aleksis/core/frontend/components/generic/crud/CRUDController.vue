<!-- TODO: Add disable on loading to CRUDBar & disable CRUDBar if dialog open. -->

<script setup>
import { computed, reactive, ref, useAttrs, toRef, toRefs } from "vue";
import CRUDBar from "./CRUDBar.vue";
import {
  activeFilterCountProps,
  CRUDBarProps,
  disableProps,
} from "../../../composables/crud/useCRUDComponents.js";
import { useAction, maxActionsProps } from "../../../composables/useAction.js";
import i18n from "../../../app/i18n";

const props = defineProps({
  ...CRUDBarProps,
  ...disableProps,
  ...maxActionsProps,
  ...activeFilterCountProps,
  crud: {
    type: Object,
    required: true,
  },
  queryItems: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits([
  "promptFilters",
  "clearFilters",
  "promptCreate",
  "promptDelete",
]);
// Duplicated since defineEmits can not reference from within its scope.
const emits = ["promptFilters", "promptCreate", "promptDelete"];

// Actions
const actions = computed(() => {
  return props.additionalActions.concat(
    props.disableDelete
      ? []
      : [
          {
            name: i18n.global.t("actions.delete"),
            icon: "$deleteContent",
            predicate: (item) => item.canDelete,
            handler: (items) => emit("promptDelete", items),
            clearSelection: true,
          },
        ],
  );
});

const selectedAction = ref(undefined);

// TODO: Does this mapping and copying all items have perf problems?
const queryItems = computed(() =>
  selectedAction.value
    ? props.queryItems?.map((item) => {
        const actionName = selectedAction.value.name;
        const pred = actions.value.find(
          (action) => action.name === actionName,
        ).predicate;
        return {
          ...item,
          selectable: pred(item),
        };
      })
    : props.queryItems,
);

const selection = ref([]);

function performAction(action) {
  const actionName = action.name;
  selection.value = useAction(
    actions.value.find((action) => action.name === actionName),
    selection.value,
  );
}

const actionAttrs = {
  actions: actions,
  selectionCount: computed(() => selection.value.length),
  "onUpdate:selectedAction": (action) => (selectedAction.value = action),
  onPerformAction: performAction,
};

const searchString = ref("");

// helper
function updateValues(target, source) {
  // Copy the target object while taking the values from the source object.
  return Object.fromEntries(
    Object.keys(target).map((key) => [key, toRef(source, key)]),
  );
}

const crud = toRef(props, "crud");
const additionalActions = ref([]);
const topAttrs = reactive({
  ...toRefs(crud),
  crud,
  ...updateValues(disableProps, props),
  ...updateValues(CRUDBarProps, props),
  ...actionAttrs,
  ...updateValues(activeFilterCountProps, props),
  onPromptFilters: (filters) => emit("promptFilters", filters),
  onClearFilters: () => emit("clearFilters"),
  searchString: searchString,
  "onUpdate:searchString": (newSearchString) =>
    (searchString.value = newSearchString),
  onCreateMode: (_) => emit("promptCreate"),
  additionalActions: additionalActions,
});

const attrs = useAttrs();

const bodyAttrs = reactive({
  ...toRefs(attrs),
  queryItems,
  ...updateValues(disableProps, props),
  search: searchString,
  showSelect: selectedAction,
  selection: selection,
  "onUpdate:selection": (newSelection) => {
    selection.value = newSelection;
  },
  // Reemit the CRUDHandlers used here since they are not passed with attrs
  ...Object.fromEntries(
    emits.map((name) => [
      "on" + name.charAt(0).toUpperCase() + name.slice(1),
      (x) => emit(name, x),
    ]),
  ),
  onAdditionalActions: (newAAs) => (additionalActions.value = newAAs),
});
</script>

<template>
  <slot name="top" v-bind="topAttrs">
    <!-- TODO: actions (contain deleteByDialog) & could so far be computed by topAttrs & crud.queryResult -->
    <c-r-u-d-bar v-bind="topAttrs">
      <template #title>
        <slot name="title" />
      </template>
      <template #additionalActions="props">
        <slot name="additionalActions" v-bind="props" />
      </template>
    </c-r-u-d-bar>
  </slot>
  <slot name="body" v-bind="bodyAttrs" />
</template>
