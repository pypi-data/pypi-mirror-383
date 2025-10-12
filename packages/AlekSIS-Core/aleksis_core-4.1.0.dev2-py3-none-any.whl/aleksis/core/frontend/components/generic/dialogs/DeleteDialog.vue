<script setup>
import { computed, defineModel } from "vue";
import { getNameProps } from "../../../composables/useGetName.js";
import MobileFullscreenDialog from "./MobileFullscreenDialog.vue";
import CancelButton from "../buttons/CancelButton.vue";
import DeleteButton from "../buttons/DeleteButton.vue";

const props = defineProps({
  /**
   * Items awaiting confirmation for deletion
   */
  deleteItems: {
    type: Array,
    required: false,
    default: () => [],
  },
  loading: {
    type: Boolean,
    required: false,
    default: false,
  },
  ...getNameProps,
});

const dialogMode = defineModel("dialogMode", { type: Boolean });

defineEmits(["delete"]);

const confirmI18nKey = computed(() =>
  props.deleteItems.length > 1
    ? "actions.confirm_deletion_multiple"
    : "actions.confirm_deletion",
);

// TODO: Emit cancel again?
// TODO: Make deleteItems list selectable with radiobuttons (user can still change intend here)
// TODO: Then make deleteItems a v-model
</script>

<template>
  <mobile-fullscreen-dialog
    v-model:dialog-mode="dialogMode"
    :close-button="false"
  >
    <template #activator="props">
      <!-- @slot Insert component that activates the dialog-object-form -->
      <slot name="activator" v-bind="props"></slot>
    </template>
    <template #title>
      <!-- @slot Delete dialog title slot -->
      <slot name="title">
        {{ $t(confirmI18nKey) }}
      </slot>
    </template>
    <template #content>
      <!-- @slot Delete dialog body slot -->
      <slot name="body">
        <ul class="text-body-1">
          <li v-for="(item, i) in props.deleteItems" :key="i">
            {{ props.getNameOfItem(item, props.nameAttribute) }}
          </li>
        </ul>
      </slot>
    </template>
    <template #actions>
      <cancel-button @click="dialogMode = false" :disabled="props.loading">
        <!-- @slot Delete dialog cancel button slot -->
        <slot name="cancelContent">
          <v-icon start>$cancel</v-icon>
          {{ $t("actions.cancel") }}
        </slot>
      </cancel-button>
      <delete-button
        @click="$emit('delete', props.deleteItems)"
        :loading="props.loading"
      >
        <!-- @slot Delete dialog delete button slot -->
        <slot name="deleteContent" />
      </delete-button>
    </template>
  </mobile-fullscreen-dialog>
</template>
