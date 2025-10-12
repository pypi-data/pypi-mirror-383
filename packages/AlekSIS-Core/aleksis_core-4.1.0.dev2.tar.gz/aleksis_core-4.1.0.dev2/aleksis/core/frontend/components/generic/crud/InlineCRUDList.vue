<script setup>
import { computed, ref, useSlots, reactive } from "vue";
import {
  generateFields,
  transformObjectSchemaToTableHeaders,
} from "../../../composables/crud/useObjectForm.js";
import { objectSchemaProp } from "../../../composables/crud/useObjectFormProps.js";

import CRUDList from "./CRUDList.vue";
import EditButton from "../buttons/EditButton.vue";
import CancelButton from "../buttons/CancelButton.vue";
import SaveButton from "../buttons/SaveButton.vue";
import Field from "./form/Field.vue";

const props = defineProps({
  ...objectSchemaProp,
  patch: {
    type: Function,
    required: true,
  },
  patchLoading: {
    type: Boolean,
    required: true,
  },
  patchOnDone: {
    type: Function,
    required: true,
  },
});

const emit = defineEmits(["additionalActions"]);

const editMode = ref(false);
const valid = ref(false);

const slots = useSlots();
// TODO: Do not generate before edit requested
const fields = generateFields(props.objectSchema, slots);
let patches = undefined;

function handleSave() {
  props.patch({ input: Object.values(patches) });
}
function setEditMode(mode) {
  editMode.value = mode;
  patches = reactive({});
  if (mode) {
    emit("additionalActions", [
      {
        component: CancelButton,
        props: {
          onClick: () => setEditMode(false),
        },
      },
      {
        component: SaveButton,
        props: {
          onClick: handleSave,
          loading: props.patchLoading,
          disabled: computed(() => !valid.value).value,
        },
      },
    ]);
  } else {
    emit("additionalActions", [
      {
        component: EditButton,
        props: {
          onClick: () => setEditMode(true),
        },
      },
    ]);
  }
}

props.patchOnDone(() => {
  setEditMode(false);
});
// TODO: Should we disable editMode on error as well?

// Emit additionalActions once
setEditMode(false);

const headers = computed(() =>
  transformObjectSchemaToTableHeaders(props.objectSchema),
);

const editHeaders = computed(() => (editMode.value ? headers.value : []));

function columnSlot(key) {
  return "item." + key;
}

function handleFieldUpdate(id, key, value) {
  console.log("handleFieldUpdate", id, key, value);
  patches[id] ??= { id: id };
  patches[id][key] = value;
}
// TODO: Do not show EditButton if disableEdit
</script>

<template>
  <v-form v-model="valid">
    <c-r-u-d-list
      v-bind="$attrs"
      :object-schema="props.objectSchema"
      :headers="headers"
      disable-edit
    >
      <template v-for="(_, slot) of $slots" #[slot]="props" :key="slot">
        <slot :name="slot" v-bind="props" />
      </template>

      <template
        v-for="header in editHeaders"
        #[columnSlot(header.key)]="props"
        :key="header.key"
      >
        <field
          :field="fields[header.key]"
          :item="props.item"
          :model-value="
            patches?.[props.item.id]?.[header.key] || props.item[header.key]
          "
          @update:model-value="
            handleFieldUpdate(props.item.id, header.key, $event)
          "
        />
      </template>
    </c-r-u-d-list>
  </v-form>
</template>
