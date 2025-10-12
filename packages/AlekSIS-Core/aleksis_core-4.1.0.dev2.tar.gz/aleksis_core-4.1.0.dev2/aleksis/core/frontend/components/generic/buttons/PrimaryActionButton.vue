<script>
import BaseButton from "./BaseButton.vue";
export default {
  name: "PrimaryActionButton",
  components: { BaseButton },
  extends: BaseButton,
  props: {
    i18nKey: {
      type: String,
      required: true,
    },
    color: {
      type: String,
      required: false,
      default: "primary",
    },
  },
};
</script>
