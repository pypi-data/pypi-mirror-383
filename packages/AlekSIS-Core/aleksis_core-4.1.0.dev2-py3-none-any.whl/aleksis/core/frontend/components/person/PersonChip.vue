<script>
import AvatarContent from "./AvatarContent.vue";

export default {
  name: "PersonChip",
  components: { AvatarContent },
  extends: "v-chip",
  props: {
    person: {
      type: Object,
      required: true,
    },
    noLink: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  computed: {
    href() {
      return this.noLink
        ? undefined
        : {
            name: "core.personById",
            params: {
              id: this.person.id,
            },
          };
    },
  },
};
</script>

<template>
  <v-chip :to="href" v-bind="$attrs">
    <v-avatar start>
      <avatar-content
        :id="person.id"
        :image-url="person.avatarContentUrl"
        contain
      />
    </v-avatar>
    {{ person.shortName || person.fullName }}
  </v-chip>
</template>

<style scoped></style>
