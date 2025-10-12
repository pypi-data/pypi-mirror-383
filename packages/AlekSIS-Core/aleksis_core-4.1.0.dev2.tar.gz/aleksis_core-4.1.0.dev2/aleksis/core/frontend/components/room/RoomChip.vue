<script>
export default {
  name: "RoomChip",
  props: {
    room: {
      type: Object,
      required: true,
    },
  },
};
</script>

<template>
  <v-tooltip location="bottom">
    <template #activator="{ props }">
      <v-chip v-bind="{ ...props, ...$attrs }">
        <v-avatar>
          <v-icon> mdi-door </v-icon>
        </v-avatar>
        {{ room.shortName }}
      </v-chip>
    </template>
    <span>{{ room.name }}</span>
  </v-tooltip>
</template>
