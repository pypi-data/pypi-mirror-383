<script>
import PrimaryActionButton from "./PrimaryActionButton.vue";

export default {
  name: "DeleteButton",
  extends: PrimaryActionButton,
  props: {
    iconText: {
      type: String,
      required: false,
      default: "$deleteContent",
    },
    i18nKey: {
      type: String,
      required: false,
      default: "actions.delete",
    },
  },
};
</script>
