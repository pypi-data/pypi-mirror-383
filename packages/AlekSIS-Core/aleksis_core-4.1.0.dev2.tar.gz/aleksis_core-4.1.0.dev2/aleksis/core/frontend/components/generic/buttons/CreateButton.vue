<script>
import PrimaryActionButton from "./PrimaryActionButton.vue";

export default {
  name: "CreateButton",
  extends: PrimaryActionButton,
  props: {
    iconText: {
      type: String,
      required: false,
      default: "$plus",
    },
    i18nKey: {
      type: String,
      required: false,
      default: "actions.create",
    },
  },
};
</script>
