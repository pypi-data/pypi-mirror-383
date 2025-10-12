export default {
  props: {
    context: {
      type: String,
      default: "",
      required: false,
    },
    widget: {
      type: Object,
      required: true,
    },
  },
};
