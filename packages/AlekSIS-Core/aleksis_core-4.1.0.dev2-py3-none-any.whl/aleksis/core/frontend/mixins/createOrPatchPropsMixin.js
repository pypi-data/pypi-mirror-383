import mutatePropsMixin from "./mutatePropsMixin";

/**
 * This mixin provides item creation or update via graphQL.
 */
export default {
  mixins: [mutatePropsMixin],
  props: {
    // UPDATE NOTICE: This has the same props the DialogObjectForm used previously
    /**
     * If isCreate is true the save method will create the object or
     * patch it otherwise
     * @values true, false
     */
    isCreate: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * The graphQL create mutation
     */
    gqlCreateMutation: {
      type: Object,
      required: false,
      default: undefined,
    },
    /**
     * The graphQL patch mutation
     */
    gqlPatchMutation: {
      type: Object,
      required: false,
      default: undefined,
    },
    /**
     * An optional function to transform a single object prior to creating it
     * @values function
     */
    getCreateData: {
      type: Function,
      required: false,
      default: (item) => item,
    },
    /**
     * An optional function to transform a single object prior to patching it
     * @values function
     */
    getPatchData: {
      type: Function,
      required: false,
      default: (item) => item,
    },
  },
  computed: {
    createOrPatchProps() {
      return {
        ...this.mutateProps,
        isCreate: this.isCreate,
        gqlCreateMutation: this.gqlCreateMutation,
        gqlPatchMutation: this.gqlPatchMutation,
        getCreateData: this.getCreateData,
        getPatchData: this.getPatchData,
      };
    },
  },
};
