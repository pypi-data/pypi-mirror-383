<!-- The CRUDProvider provides the crud operations to its structured slots with useful defaults. -->
<!-- If you need a more general component use useCRUD and CRUDProps directly in your component instead. -->

<script setup>
import {
  computed,
  reactive,
  ref,
  useAttrs,
  useSlots,
  toRef,
  toRefs,
  watch,
} from "vue";
import { CRUDProps, useCRUD } from "../../../composables/crud/useCRUD.js";
import { disableProps } from "../../../composables/crud/useCRUDComponents.js";
import { fillObjectSchemaWithDefaults } from "../../../composables/crud/useObjectForm.js";
import { objectFormProps } from "../../../composables/crud/useObjectFormProps.js";
import { getNameProps } from "../../../composables/useGetName.js";
import FilterDialog from "../dialogs/FilterDialog.vue";
import DialogObjectForm from "../dialogs/DialogObjectForm.vue";
import DeleteDialog from "../dialogs/DeleteDialog.vue";
import CRUDController from "./CRUDController.vue";
import CRUDList from "./CRUDList.vue";
import InlineCRUDList from "./InlineCRUDList.vue";

const props = defineProps({
  ...CRUDProps,
  ...disableProps,
  // TODO: objectFormProps contains already editItem!
  ...objectFormProps,
  ...getNameProps,
  disableInlineEdit: {
    type: Boolean,
    required: false,
    default: false,
  },
  // Expose create, patch, delete by dialog to the parent
  createItem: {
    type: [Object, Boolean],
    required: false,
    default: false,
  },
  patchItem: {
    type: [Object, Boolean],
    required: false,
    default: false,
  },
  deleteItems: {
    type: [Array, Boolean],
    required: false,
    default: false,
  },
});
const objectSchema = computed(() =>
  fillObjectSchemaWithDefaults(props.objectSchema),
);
console.log("CRUDProvider full objectSchema:", objectSchema.value);

// Use query and mutations from props or objectSchema
function comparableToRef(object, key) {
  return object[key] && toRef(object, key);
}
const graphql = Object.fromEntries(
  Object.keys(CRUDProps).map((key) => [
    key,
    computed(() => props[key] || objectSchema.value[key]),
  ]),
);
console.log("GRAPHQL", graphql);
const crud = useCRUD({ ...graphql, objectSchema });
console.log("CRUD", crud, crud.queryItems);

const slots = useSlots();
const filterRef = ref(null);

const emit = defineEmits(["createDone", "patchDone", "deleteDone"]);

const staticDisable = {
  disableQuery: computed(() => props.disableQuery || !graphql.query.value),
  disableFilter: computed(
    () => props.disableQuery || !graphql.query.value || !("filters" in slots),
  ),
  disableSearch: computed(() => props.disableQuery || !graphql.query.value),
  disableActions: computed(() => props.disableQuery || !graphql.query.value),
  disableCreate: computed(
    () => props.disableCreate || !graphql.createMutation.value,
  ),
  disablePatch: computed(
    () => props.disablePatch || !graphql.patchMutation.value,
  ),
  disableDelete: computed(
    () => props.disableDelete || !graphql.deleteMutation.value,
  ),
};
staticDisable.disableEdit = computed(
  () => staticDisable.disableCreate.value && staticDisable.disablePatch.value,
);

// TODO: Also check general permission?
const dynamicDisable = reactive({
  ...staticDisable,
  disablePatch: computed(
    () =>
      staticDisable.disablePatch.value ||
      !(
        crud.queryItems?.value && crud.queryItems?.value.some((i) => i.canEdit)
      ),
  ),
  disableDelete: computed(
    () =>
      staticDisable.disableDelete.value ||
      !(
        crud.queryItems?.value &&
        crud.queryItems?.value.some((i) => i.canDelete)
      ),
  ),
});

const MODES = {
  DEFAULT: 0,
  CREATE: 1,
  PATCH: 2,
  DELETE: 3,
  FILTER: 4,
};

const mode = ref(MODES.DEFAULT);

function resetMode(newMode) {
  // Mode can only close itself.
  if (!newMode) {
    mode.value = MODES.DEFAULT;
  }
}

// TODO: After all parts are seperated now, they could be put in a or several composables returning CRUDAttrs, attrs and extra

function useFilterComponent() {
  // TODO: Pass default filters via prop?
  const activeFilters = ref({});

  function clearFilters() {
    console.log(filterRef, filterRef.value);
    filterRef.value.clearFilters();
  }

  function setFilters(filters) {
    console.log("SET", filters);
    resetMode();
    activeFilters.value = filters;
    // queryVariables should be deeply reactive and this should work in all cases
    crud.queryVariables.value.filters = JSON.stringify(filters);
    crud.queryRefetch(crud.queryVariables.value);
  }

  const filterAttrs = reactive({
    objectSchema: objectSchema,
    dialogMode: computed(() => mode.value === MODES.FILTER),
    "onUpdate:dialogMode": resetMode,
    ref: filterRef,
    "onUpdate:modelValue": setFilters,
  });

  function promptFilters(filters) {
    if (filters) {
      activeFilters.value = filters;
    }
    mode.value = MODES.FILTER;
  }

  return {
    filterAttrs,
    bodyFilterAttrs: {
      activeFilterCount: computed(
        () => Object.keys(activeFilters.value).length,
      ),
      onClearFilters: clearFilters,
      onPromptFilters: promptFilters,
    },
  };
}

function useEditComponent(disableCreate, disablePatch) {
  console.log("useEditComponent");
  // no default => undefined
  const defaultItem = computed(() =>
    Object.fromEntries(
      Object.entries(objectSchema.value.properties || {})
        .filter(([_, val]) => !val.hide)
        .map(([name, val]) => [name, val.default]),
    ),
  );

  const createItem = ref(false);
  const patchItem = ref(false);
  const id = ref(false);

  function extractItemId(item) {
    function idOrValue(val) {
      return Array.isArray(val) ? val.map(idOrValue) : val?.id || val;
    }

    return Object.fromEntries(
      Object.entries(item).map(([key, val]) => [key, idOrValue(val)]),
    );
  }

  function handlePatch(patch) {
    if (mode.value === MODES.CREATE) {
      crud.create({
        input: [
          {
            ...extractItemId(defaultItem.value),
            ...extractItemId(createItem.value),
            ...patch,
          },
        ],
      });
    } else if (mode.value === MODES.PATCH) {
      // TODO: I do not like this handling of ID here too much -> Find a more general mechanism? Maybe when thinking about hide?
      crud.patch({ input: [{ ...patch, id: id.value }] });
    } else {
      console.error("Wow this should not happen:", mode.value);
    }
  }

  // TODO: Properly seperate create & patch. Not just do it here!
  if (!disableCreate) {
    crud.createOnDone(({ data }) => {
      if (mode.value === MODES.CREATE) {
        resetMode();
        createItem.value = false;
      }
      emit("createDone", data);
    });
  }
  if (!disablePatch) {
    crud.patchOnDone(({ data }) => {
      if (mode.value === MODES.PATCH) {
        resetMode();
        patchItem.value = false;
      }
      emit("patchDone", data);
    });
  }

  const editAttrs = reactive({
    objectSchema: objectSchema,
    objectLayout: toRef(props, "objectLayout"),
    dialogMode: computed(
      () => mode.value === MODES.CREATE || mode.value === MODES.PATCH,
    ),
    "onUpdate:dialogMode": resetMode,
    editItem: computed(() => {
      if (mode.value === MODES.CREATE) {
        return createItem.value;
      } else if (mode.value === MODES.PATCH) {
        return patchItem.value;
      } else {
        return {};
      }
    }),
    // TODO: Do not update createItem otherwise props passed via it and not set in edit are not passed to create function.
    // Deactivate as a fix since this update is not needed currently.
    // "onUpdate:editItem": (item) => {
    //   if (mode.value === MODES.CREATE) {
    //     createItem.value = item;
    //   } else if (mode.value === MODES.PATCH) {
    //     patchItem.value = item;
    //   }
    // },
    onPatch: handlePatch,
    loading: computed(() => {
      if (mode.value === MODES.CREATE) {
        return crud.createLoading.value;
      } else if (mode.value === MODES.PATCH) {
        return crud.patchLoading.value;
      } else {
        return false;
      }
    }),
  });

  const editFieldSlots = Object.fromEntries(
    Object.entries(slots).filter(([slot, _]) => slot.endsWith(".field")),
  );

  function promptCreate(item) {
    createItem.value = item || createItem.value || defaultItem.value;
    mode.value = MODES.CREATE;
  }

  watch(
    () => props.createItem,
    (item) => {
      if (item) {
        promptCreate(item);
      }
    },
  );

  function promptPatch(item) {
    patchItem.value = item || patchItem.value;
    id.value = patchItem.value.id;
    if (!patchItem.value) {
      console.warn("Promted for patch without a patchItem.");
    } else {
      mode.value = MODES.PATCH;
    }
  }

  watch(
    () => props.patchItem,
    (item) => {
      if (item) {
        promptPatch(item);
      }
    },
  );

  return {
    editAttrs,
    editFieldSlots,
    bodyEditAttrs: {
      onPromptCreate: promptCreate,
      onPromptPatch: promptPatch,
    },
  };
}

function useDeleteComponent() {
  crud.deleteOnDone(() => {
    if (mode.value === MODES.DELETE) {
      resetMode();
      deleteItems.value = [];
    }
    emit("deleteDone");
  });

  const deleteItems = ref([]);

  const deleteAttrs = reactive({
    objectSchema: objectSchema,
    dialogMode: computed(() => mode.value === MODES.DELETE),
    "onUpdate:dialogMode": resetMode,
    deleteItems: deleteItems,
    onDelete: (items) => crud.delete({ ids: items.map((item) => item.id) }),
    loading: computed(() => {
      if (mode.value === MODES.DELETE) {
        return crud.deleteLoading.value;
      } else {
        return false;
      }
    }),
    ...Object.fromEntries(
      Object.keys(getNameProps).map((key) => [key, toRef(props, key)]),
    ),
  });

  function promptDelete(items) {
    if (!items) {
      console.warn("Promted for delete but no items were given.");
    }
    deleteItems.value = items;
    mode.value = MODES.DELETE;
  }

  watch(
    () => props.deleteItems,
    (items) => {
      console.log("deleteItems watcher triggered", items);
      if (items && items.length > 0) {
        promptDelete(items);
      }
    },
  );

  return {
    deleteAttrs,
    bodyDeleteAttrs: {
      onPromptDelete: promptDelete,
    },
  };
}

const { filterAttrs, bodyFilterAttrs } = !staticDisable.disableFilter.value
  ? useFilterComponent()
  : {};
const { editAttrs, editFieldSlots, bodyEditAttrs } = !staticDisable.disableEdit
  .value
  ? useEditComponent(
      staticDisable.disableCreate.value,
      staticDisable.disablePatch.value,
    )
  : {};
const { deleteAttrs, bodyDeleteAttrs } = !staticDisable.disableDelete.value
  ? useDeleteComponent()
  : {};
const bodyAttrs = reactive({
  ...toRefs(useAttrs()),
  objectSchema: objectSchema,
  ...crud,
  crud,
  ...toRefs(dynamicDisable),
  loading: crud.queryLoading,
  disabled: computed(
    () =>
      props.disabled.value ||
      crud.queryLoading.value ||
      mode.value !== MODES.DEFAULT,
  ),
  ...bodyFilterAttrs,
  ...bodyEditAttrs,
  ...bodyDeleteAttrs,
});
</script>

<template>
  <slot
    name="filterComponent"
    v-if="!dynamicDisable.disableFilter"
    v-bind="filterAttrs"
  >
    <filter-dialog v-bind="filterAttrs" ref="filterRef">
      <template #filters="props">
        <slot name="filters" v-bind="props" />
      </template>
    </filter-dialog>
  </slot>

  <slot
    name="editComponent"
    v-if="!dynamicDisable.disableEdit"
    v-bind="editAttrs"
  >
    <dialog-object-form v-bind="editAttrs">
      <template v-for="(_, slot) of editFieldSlots" #[slot]="scope">
        <slot :name="slot" v-bind="scope" />
      </template>
    </dialog-object-form>
  </slot>

  <slot
    name="deleteComponent"
    v-if="!dynamicDisable.disableDelete"
    v-bind="deleteAttrs"
  >
    <delete-dialog v-bind="deleteAttrs" />
  </slot>

  <slot name="body" v-bind="bodyAttrs">
    <c-r-u-d-controller v-if="!dynamicDisable.disableQuery" v-bind="bodyAttrs">
      <template #additionalActions="props">
        <slot name="additionalActions" v-bind="props" />
      </template>
      <template #body="bodyProps">
        <slot name="view" v-bind="bodyProps">
          <!-- TODO: Both select slots? -->
          <c-r-u-d-list v-if="props.disableInlineEdit" v-bind="bodyProps">
            <template v-for="(_, slot) of $slots" #[slot]="props">
              <slot :name="slot" v-bind="props" />
            </template>
          </c-r-u-d-list>
          <inline-c-r-u-d-list v-else v-bind="bodyProps">
            <template v-for="(_, slot) of $slots" #[slot]="props">
              <slot :name="slot" v-bind="props" />
            </template>
          </inline-c-r-u-d-list>
        </slot>
      </template>
    </c-r-u-d-controller>
  </slot>
</template>
