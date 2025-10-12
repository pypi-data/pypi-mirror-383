<template>
  <template v-if="groups.length">
    <v-list-item
      v-bind="$attrs"
      v-for="group in groups"
      :key="group.id"
      :to="{ name: 'core.group', params: { id: group.id } }"
    >
      <template #prepend>
        <v-avatar>
          <avatar-content v-if="group.avatarUrl" :image-url="group.avatarUrl" />
        </v-avatar>
      </template>

      <v-list-item-title>
        {{ group.name }}
        <span v-if="group.schoolTerm && group.schoolTerm.name">
          ({{ group.schoolTerm.name }})
        </span>
      </v-list-item-title>
    </v-list-item>
  </template>
  <template v-else>
    <v-list-item>
      <v-list-item-title>
        {{ $t("group.no_groups") }}
      </v-list-item-title>
    </v-list-item>
  </template>
</template>

<script>
import AvatarContent from "../person/AvatarContent.vue";

export default {
  name: "GroupList",
  components: { AvatarContent },
  props: {
    groups: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style scoped></style>
