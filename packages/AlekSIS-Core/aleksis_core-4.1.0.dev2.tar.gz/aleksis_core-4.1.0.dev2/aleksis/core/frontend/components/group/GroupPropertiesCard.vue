<script setup>
import GroupCollection from "./GroupCollection.vue";
</script>
<script>
export default {
  name: "GroupPropertiesCard",
  props: {
    group: {
      type: Object,
      required: true,
    },
  },
};
</script>

<template>
  <v-card>
    <v-card-title>{{ $t("group.properties") }}</v-card-title>

    <v-list lines="two">
      <v-list-item prepend-icon="$groupType">
        <v-list-item-title>
          {{ group.groupType?.name || $t("group.group_type.no_group_type") }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ $t("group.group_type.title") }}
        </v-list-item-subtitle>
      </v-list-item>
      <v-divider inset />

      <v-list-group>
        <template #activator="{ props }">
          <v-list-item
            v-bind="props"
            :disabled="group.childGroups.length === 0"
            :append-icon="group.childGroups.length === 0 ? null : undefined"
          >
            <template #prepend>
              <v-icon>mdi-subdirectory-arrow-right</v-icon>
            </template>
            <v-list-item-title>
              {{ $t("group.child_groups_n", group.childGroups.length) }}
            </v-list-item-title>
          </v-list-item>
        </template>
        <group-collection :groups="group.childGroups" dense />
      </v-list-group>

      <v-list-group>
        <template #activator="{ props }">
          <v-list-item
            v-bind="props"
            prepend-icon="mdi-file-tree-outline"
            :title="$t('group.parent_groups_n', group.parentGroups.length)"
            :disabled="group.parentGroups.length === 0"
            :append-icon="group.parentGroups.length === 0 ? null : undefined"
          />
        </template>
        <group-collection :groups="group.parentGroups" dense />
      </v-list-group>
    </v-list>
  </v-card>
</template>

<style scoped></style>
