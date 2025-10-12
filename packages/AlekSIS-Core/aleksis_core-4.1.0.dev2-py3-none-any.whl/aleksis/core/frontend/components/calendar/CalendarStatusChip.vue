<script>
export default {
  name: "CalendarStatusChip",
  props: {
    color: {
      type: String,
      required: true,
    },
    icon: {
      type: String,
      required: true,
    },
  },
};
</script>

<template>
  <v-chip :color="color" label>
    <v-avatar start>
      <v-icon>{{ icon }}</v-icon>
    </v-avatar>
    <slot></slot>
  </v-chip>
</template>
