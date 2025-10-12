<script setup>
import { ref, defineModel, computed, watch } from "vue";
import MobileFullscreenDialog from "./MobileFullscreenDialog.vue";
import ObjectForm from "../crud/ObjectForm.vue";
import SaveButton from "../buttons/SaveButton.vue";
import CancelButton from "../buttons/CancelButton.vue";

const props = defineProps({
  title: {
    type: String,
    required: false,
    default: "",
  },
  loading: {
    type: Boolean,
    required: false,
    default: false,
  },
});

const dialogMode = defineModel("dialogMode");
// TODO: emits are same as ObjectForm; share them?
const emit = defineEmits(["update:editItem", "patch"]);

// TODO: Emit cancel & save again? But for save I do not have any items anymore!

const patch = ref({});
const doPatch = () => {
  emit("patch", patch.value);
};
const valid = computed(() => {
  return Object.keys(patch.value).length > 0;
});
watch(dialogMode.value, () => {
  if (!dialogMode.value) {
    patch.value = {};
  }
});
function updatePatch(data) {
  patch.value = data;
}
</script>

<template>
  <mobile-fullscreen-dialog
    v-model:dialog-mode="dialogMode"
    max-width="555px"
    :close-button="false"
  >
    <template #activator="props">
      <!-- @slot Insert component that activates the dialog-object-form -->
      <slot name="activator" v-bind="props" />
    </template>

    <template #title>
      <!-- @slot The title of the dialog-object-form -->
      <slot name="title">
        <span class="text-h5">
          {{ props.title }}
        </span>
      </slot>
    </template>

    <template #content>
      <object-form
        v-bind="$attrs"
        @update:edit-item="$emit('update:editItem', $event)"
        @patch="updatePatch"
        @save="doPatch"
      >
        <template v-for="(_, slot) of $slots" #[slot]="scope"
          ><slot :name="slot" v-bind="scope" />
        </template>
      </object-form>
    </template>

    <template #actions>
      <cancel-button @click="dialogMode = false" :disabled="props.loading" />
      <save-button
        type="submit"
        @click="doPatch"
        :loading="props.loading"
        :disabled="!valid"
        class="ml-2"
      />
    </template>
  </mobile-fullscreen-dialog>
</template>
