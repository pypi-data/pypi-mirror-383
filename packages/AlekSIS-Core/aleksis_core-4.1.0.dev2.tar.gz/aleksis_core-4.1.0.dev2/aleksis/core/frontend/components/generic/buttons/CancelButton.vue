<script>
import SecondaryActionButton from "./SecondaryActionButton.vue";

export default {
  name: "CancelButton",
  extends: SecondaryActionButton,
  props: {
    iconText: {
      type: String,
      required: false,
      default: "$cancel",
    },
    i18nKey: {
      type: String,
      required: false,
      default: "actions.cancel",
    },
    color: {
      type: String,
      required: false,
      default: "error",
    },
  },
};
</script>
