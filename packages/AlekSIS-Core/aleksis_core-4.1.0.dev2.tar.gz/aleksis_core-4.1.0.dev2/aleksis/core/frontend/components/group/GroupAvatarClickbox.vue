<template>
  <avatar-click-box>
    <template #image>
      <avatar-content :image-url="url" contain />
    </template>
  </avatar-click-box>
</template>

<script>
import AvatarContent from "../person/AvatarContent.vue";

export default {
  name: "GroupAvatarClickBox",
  components: {
    AvatarContent,
  },
  props: {
    url: {
      type: String,
      required: true,
    },
  },
};
</script>
