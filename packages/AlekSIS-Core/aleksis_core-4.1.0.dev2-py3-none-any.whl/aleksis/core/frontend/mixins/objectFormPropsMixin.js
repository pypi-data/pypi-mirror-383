import createOrPatchPropsMixin from "./createOrPatchPropsMixin";

export default {
  mixins: [createOrPatchPropsMixin],
  props: {
    /**
     * Defines if Object form creates or edits items. If undefined this is decided implicitly depending on editItem.
     * @values undefined, true, false
     */
    isCreate: {
      type: Boolean,
      required: false,
      default: undefined,
    },
    /**
     * Title if isCreate is true
     */
    createItemI18nKey: {
      type: String,
      required: false,
      default: "actions.create",
    },
    /**
     * Title if isCreate is false
     */
    editItemI18nKey: {
      type: String,
      required: false,
      default: "actions.edit",
    },
    /**
     * SuccessMessage if isCreate is true
     */
    createSuccessMessageI18nKey: {
      type: String,
      required: false,
      default: "status.object_create_success",
    },
    /**
     * SuccessMessage if
     */
    editSuccessMessageI18nKey: {
      type: String,
      required: false,
      default: "status.object_edit_success",
    },
    /**
     * Fields in dialog-object-form
     *
     * @values list of field objects
     * @example [{text: "Field text", value: "Field value name"} ...]
     */
    fields: {
      type: Array,
      required: true,
    },
    /**
     * Default item used for creation if isCreate is true
     */
    defaultItem: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    /**
     * Item offered for editing if isCreate is false
     */
    editItem: {
      type: Object,
      required: false,
      default: null,
    },
    /**
     * Update dialog from defaultItem or editItem also if dialog is shown
     * This would happen only on mount and if dialog is hidden otherwise.
     */
    forceModelItemUpdate: {
      type: Boolean,
      required: false,
      default: false,
    },
    /**
     * When used for editing send a only the changes not the whole editObject.
     * Mimics the behaviour of the InlineCRUDList.
     */
    minimalPatch: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  computed: {
    objectFormProps() {
      return {
        ...this.createOrPatchProps,
        createItemI18nKey: this.createItemI18nKey,
        editItemI18nKey: this.editItemI18nKey,
        createSuccessMessageI18nKey: this.createSuccessMessageI18nKey,
        editSuccessMessageI18nKey: this.editSuccessMessageI18nKey,
        fields: this.fields,
        defaultItem: this.defaultItem,
        editItem: this.editItem,
        forceModelItemUpdate: this.forceModelItemUpdate,
        minimalPatch: this.minimalPatch,
      };
    },
  },
};
