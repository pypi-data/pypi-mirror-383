<script>
import BaseButton from "./BaseButton.vue";
export default {
  name: "IconButton",
  components: { BaseButton },
  extends: BaseButton,
  props: {
    icon: {
      required: false,
      default: true,
      type: Boolean,
    },
    variant: {
      type: String,
      required: false,
      default: "text",
    },
  },
};
</script>
