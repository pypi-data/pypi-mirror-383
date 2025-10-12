import createOrPatchMixin from "./createOrPatchMixin";
import objectFormPropsMixin from "./objectFormPropsMixin";

export default {
  mixins: [createOrPatchMixin, objectFormPropsMixin],
  data() {
    return {
      valid: false,
      firstInitDone: false,
      itemModel: {},
      editPatch: {},
    };
  },
  methods: {
    dynamicSetter(item, fieldName) {
      return (value) => {
        this.$set(item, fieldName, value);
        if (this.minimalPatch && !this.isCreate) {
          this.$set(this.editPatch, this.itemId, item.id);
          this.$set(this.editPatch, fieldName, value);
        }
      };
    },
    buildExternalSetter(item) {
      return (fieldName, value) => this.dynamicSetter(item, fieldName)(value);
    },
    buildAttrs(item, field) {
      return {
        dense: true,
        filled: true,
        value: item[field.value],
        modelValue: item[field.value],
        inputValue: item[field.value],
        label: field.text,
        disabled: field?.disabled,
      };
    },
    buildOn(setter) {
      return {
        input: setter,
        change: setter,
        replace: setter,
      };
    },
    buildProps(item, field) {
      const attrs = this.buildAttrs(item, field);
      const setter = this.dynamicSetter(item, field.value);
      attrs.onInput = setter;
      attrs.onChange = setter;
      attrs.onReplace = setter;
      attrs["onUpdate:modelValue"] = setter;
    },
    cancel() {
      /**
       * Emitted when user cancels
       */
      this.$emit("cancel");
    },
    handleSuccess() {
      let snackbarTextKey = this.isCreate
        ? this.createSuccessMessageI18nKey
        : this.editSuccessMessageI18nKey;

      this.$toastSuccess(this.$t(snackbarTextKey));
      this.resetModel();
    },
    resetModel() {
      // Handle isCreate undefined, by deciding on the presence of editItem
      //   This implicit behaviour often makes more sense
      //   and doing it higher up (in parent) makes parent less flexible.
      //   Specifically not working anymore with CRUD.
      if (!this.isCreate) {
        this.isCreate = !this.editItem;
      }
      this.itemModel = JSON.parse(
        JSON.stringify(this.isCreate ? this.defaultItem : this.editItem),
      );
      this.editPatch = {};
    },
    updateModel() {
      // Only update the model if the dialog is hidden or has just been mounted
      if (this.forceModelItemUpdate || !this.firstInitDone || !this.dialog) {
        this.resetModel();
      }
    },
    submit() {
      if (this.minimalPatch && !this.isCreate) {
        this.createOrPatch([this.editPatch]);
      } else {
        this.createOrPatch([this.itemModel]);
      }
    },
  },
  mounted() {
    this.$on("save", this.handleSuccess);

    this.updateModel();
    this.firstInitDone = true;

    this.$watch("isCreate", this.updateModel);
    this.$watch("defaultItem", this.updateModel, { deep: true });
    this.$watch("editItem", this.updateModel, { deep: true });
  },
  computed: {
    title() {
      return this.isCreate
        ? this.$t(this.createItemI18nKey)
        : this.$t(this.editItemI18nKey);
    },
    internalValid() {
      return (
        !!this.valid &&
        (this.minimalPatch && !this.isCreate
          ? Object.keys(this.editPatch).length > 0
          : true)
      );
    },
  },
  watch: {
    internalValid(valid) {
      this.$emit("update:valid", valid);
    },
  },
};
