import mutateMixin from "../../../mixins/mutateMixin";

export default {
  mixins: [mutateMixin],
  props: {
    widget: {
      type: Object,
      required: true,
    },
  },
};
