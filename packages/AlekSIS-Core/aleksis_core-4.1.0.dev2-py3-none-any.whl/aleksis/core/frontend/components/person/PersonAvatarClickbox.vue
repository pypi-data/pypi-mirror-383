<template>
  <avatar-click-box>
    <template #image>
      <avatar-content :id="id" contain />
    </template>
  </avatar-click-box>
</template>

<script>
import AvatarContent from "./AvatarContent.vue";

export default {
  name: "PersonAvatarClickBox",
  components: {
    AvatarContent,
  },
  data: () => ({
    overlay: false,
  }),
  props: {
    id: {
      type: String,
      required: false,
      default: "",
    },
  },
};
</script>

<style scoped></style>
