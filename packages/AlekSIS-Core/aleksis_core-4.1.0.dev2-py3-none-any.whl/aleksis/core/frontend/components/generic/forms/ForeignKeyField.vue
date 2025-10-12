<template>
  <v-autocomplete
    v-bind="$attrs"
    :items="items"
    item-value="id"
    :item-title="itemName"
    :chips="chips"
    :multiple="multiple"
    class="fc-my-auto"
  >
    <template #prepend-inner>
      <slot name="prepend-inner" />
    </template>
    <template v-if="!multiple" #item="data">
      <slot name="item" v-bind="data">
        {{ getItemText(data.item) }}
      </slot>
    </template>
    <template v-if="!chips" #chip="data">
      <slot name="selection" v-bind="data">
        {{ getItemText(data.item) }}
      </slot>
    </template>
    <template #progress>
      <slot name="progress" />
    </template>
    <template #append-outer v-if="enableCreate">
      <icon-button
        @click="createMode = true"
        icon-text="$plus"
        i18n-key="actions.create"
      />

      <slot
        name="createComponent"
        :attrs="{
          value: createMode,
          defaultItem: $attrs['default-item'],
          gqlQuery: lastQuery,
          gqlCreateMutation: $attrs['gql-create-mutation'],
          gqlPatchMutation: $attrs['gql-patch-mutation'],
          isCreate: true,
          fields: $attrs['fields'],
          getCreateData: $attrs['getCreateData'],
          createItemI18nKey: $attrs['createItemI18nKey'],
          affectedQuery: lastQuery,
        }"
        :on="{
          input: (i) => (createMode = i),
          save: handleSave,
        }"
      >
        <dialog-object-form
          v-model="createMode"
          @save="handleSave"
          :is-create="true"
          :default-item="$attrs['default-item']"
          :fields="$attrs['fields']"
          :gql-query="lastQuery"
          :gql-create-mutation="$attrs['gql-create-mutation']"
          :create-item-i18n-key="$attrs['create-item-i18n-key']"
          :get-create-data="$attrs['get-create-data']"
          :affected-query="lastQuery"
        >
          <template v-for="(_, name) in $slots" #[name]="slotData">
            <slot :name="name" v-bind="slotData" />
          </template>
        </dialog-object-form>
      </slot>

      <closable-snackbar :color="snackbarState" v-model="snackbar">
        {{ snackbarText }}
      </closable-snackbar>
    </template>
  </v-autocomplete>
</template>

<script>
import ClosableSnackbar from "../dialogs/ClosableSnackbar.vue";
import DialogObjectForm from "../dialogs/DialogObjectForm.vue";

import queryMixin from "../../../mixins/queryMixin.js";

export default {
  name: "ForeignKeyField",
  components: { ClosableSnackbar, DialogObjectForm },
  mixins: [queryMixin],
  extends: "v-autocomplete",
  data() {
    return {
      createMode: false,
      snackbar: false,
      snackbarState: "error",
      snackbarText: "",
    };
  },
  methods: {
    handleSave(items) {
      let newValues =
        "return-object" in this.$attrs ? items : items.map((item) => item.id);
      let modelValues =
        "multiple" in this.$attrs
          ? Array.isArray(this.$attrs.value)
            ? this.$attrs.value.concat(newValues)
            : newValues
          : newValues[0];

      this.$emit("input", modelValues);
    },
    slotName(field) {
      return field.value + ".field";
    },
    getItemText(item) {
      if (typeof this.itemName === "string") {
        return item[this.itemName];
      } else if (typeof this.itemName === "function") {
        return this.itemName(item);
      }
    },
  },
  props: {
    itemName: {
      type: [String, Function],
      required: false,
      default: "name",
    },
    enableCreate: {
      type: Boolean,
      required: false,
      default: true,
    },
    chips: {
      type: Boolean,
      required: false,
      default: false,
    },
    multiple: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
};
</script>

<style scoped>
.fc-my-auto > :first-child {
  margin-block: auto;
}
</style>
