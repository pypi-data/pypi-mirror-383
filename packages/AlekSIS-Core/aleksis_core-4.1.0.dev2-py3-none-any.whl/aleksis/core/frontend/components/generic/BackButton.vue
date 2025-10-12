<script>
import PrimaryActionButton from "./buttons/PrimaryActionButton.vue";

export default {
  name: "BackButton",
  extends: PrimaryActionButton,
  props: {
    iconText: {
      type: String,
      required: false,
      default: "$prev",
    },
    i18nKey: {
      type: String,
      required: false,
      default: "actions.back",
    },
    color: {
      type: String,
      required: false,
      default: "secondary",
    },
  },
};
</script>
