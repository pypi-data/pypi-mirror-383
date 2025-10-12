<script>
import SecondaryActionButton from "./SecondaryActionButton.vue";

export default {
  name: "InviteButton",
  extends: SecondaryActionButton,
  props: {
    iconText: {
      type: String,
      required: false,
      default: "$plus",
    },
    i18nKey: {
      type: String,
      required: false,
      default: "person.invite",
    },
  },
};
</script>
