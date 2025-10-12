<script setup>
import { computed } from "vue";
import i18n from "../../../app/i18n";
import { transformObjectSchemaToTableHeaders } from "../../../composables/crud/useObjectForm.js";
import { objectSchemaProp } from "../../../composables/crud/useObjectFormProps.js";
import { disableProps } from "../../../composables/crud/useCRUDComponents.js";

import EditButton from "../buttons/EditButton.vue";
import DeleteButton from "../buttons/DeleteButton.vue";
import Mascot from "../mascot/Mascot.vue";

const props = defineProps({
  ...objectSchemaProp,
  queryItems: {
    type: Array,
    required: false,
    default: () => [],
  },
  elevated: {
    type: Boolean,
    required: false,
    default: true,
  },
  disableActionColumn: {
    type: Boolean,
    required: false,
    default: false,
  },
  ...disableProps,
  headers: {
    type: Array,
    required: false,
    default: () => [],
  },
  selection: {
    type: Array,
    require: false,
    default: () => [],
  },
});

const headersWithoutInternal = computed(() => {
  return props.headers.length > 0
    ? props.headers
    : transformObjectSchemaToTableHeaders(props.objectSchema);
});

const headers = computed(() =>
  headersWithoutInternal.value.concat(
    props.disableActionColumn || (props.disablePatch && props.disableDelete)
      ? []
      : [
          {
            key: "CRUDListInternalActions",
            title: i18n.global.t("actions.title"),
            sortable: false,
            align: "end",
          },
        ],
  ),
);

const emit = defineEmits(["promptPatch", "promptDelete", "onUpdate:selection"]);

function columnSlot(key) {
  return "item." + key;
}

// TODO Alsijil: Introduce useDeepSearch. Since the new vuetify search here works different and
// I wanted to first test the new default search.
// DeepSearch is so far used only in the coursebook. When this is implemented it should implement
// a orderless regexp search as well and probably make it the default! DISCUSS.
// TODO: Reintroduce sortBy and port syncSortMixin.js Julian?
// TODO: Port itemsPerPageMixin.js?
</script>

<template>
  <v-data-table
    v-bind="$attrs"
    :headers="headers"
    :items="queryItems"
    :class="elevated ? 'elevation-2' : ''"
    :model-value="props.selection"
    @update:model-value="emit('update:selection', $event)"
    return-object
  >
    <template
      v-for="header in headersWithoutInternal"
      #[columnSlot(header.key)]="columnProps"
      :key="header.key"
    >
      <slot :name="columnSlot(header.key)" v-bind="columnProps">
        <component
          v-if="
            header.displayComponent &&
            (columnProps.item[header.key] ||
              columnProps.item[header.key] === false)
          "
          :is="header.displayComponent"
          :value="columnProps.item[header.key]"
          :object-schema="props.objectSchema.properties[header.key]"
        />
        <span v-else>{{ columnProps.item[header.key] }}</span>
      </slot>
    </template>

    <template v-for="(_, slot) of $slots" #[slot]="slotProps">
      <slot :name="slot" v-bind="slotProps ?? {}" />
    </template>

    <!-- Add a action (= btn) column -->
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #item.CRUDListInternalActions="{ item }">
      <!-- @slot Add additional action to action column -->
      <slot name="actions" :item="item" />
      <edit-button
        v-if="!props.disablePatch && 'canEdit' in item && item.canEdit"
        icon
        variant="text"
        color="secondary"
        @click="$emit('promptPatch', item)"
        :disabled="props.disabled"
      />
      <delete-button
        v-if="!props.disableDelete && 'canDelete' in item && item.canDelete"
        icon
        variant="text"
        color="error"
        @click="$emit('promptDelete', [item])"
        :disabled="props.disabled"
      />
    </template>

    <!-- Customize expanded rows -->
    <template #expanded-item="{ headers, item }">
      <td :colspan="headers.length">
        <slot name="expanded-item" :item="item" />
      </td>
    </template>

    <template #no-data>
      <slot name="no-data">
        <div class="d-flex flex-column align-center justify-center">
          <mascot type="ready_for_items" width="33%" min-width="250px" />
          <div class="mb-2">
            {{ $t("$vuetify.noDataText") }}
          </div>
        </div>
      </slot>
    </template>
  </v-data-table>
</template>
