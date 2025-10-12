<script>
import PrimaryActionButton from "./PrimaryActionButton.vue";

export default {
  name: "SaveButton",
  extends: PrimaryActionButton,
  props: {
    iconText: {
      type: String,
      required: false,
      default: "$save",
    },
    i18nKey: {
      type: String,
      required: false,
      default: "actions.save",
    },
  },
};
</script>
