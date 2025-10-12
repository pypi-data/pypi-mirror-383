export default {
  props: {
    /**
     * Dialog-mode (open or closed)
     * @model
     * @values true,false
     */
    modelValue: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  emits: ["update:modelValue"],
  data() {
    return {
      internalDialogMode: this.modelValue,
    };
  },
  computed: {
    dialogMode: {
      get() {
        return this.internalDialogMode;
      },
      set(newValue) {
        this.internalDialogMode = newValue;
        this.$emit("update:modelValue", newValue);
      },
    },
  },
  mounted() {
    this.$watch("modelValue", (newVal) => {
      this.dialogMode = newVal;
    });
  },
};
