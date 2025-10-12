<script>
import PrimaryActionButton from "./PrimaryActionButton.vue";

export default {
  name: "EditButton",
  extends: PrimaryActionButton,
  props: {
    iconText: {
      type: String,
      required: false,
      default: "$edit",
    },
    i18nKey: {
      type: String,
      required: false,
      default: "actions.edit",
    },
  },
};
</script>
