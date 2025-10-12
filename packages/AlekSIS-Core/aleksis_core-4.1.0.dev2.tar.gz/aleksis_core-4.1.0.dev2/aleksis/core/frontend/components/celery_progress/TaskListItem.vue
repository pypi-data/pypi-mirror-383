<template>
  <v-list-item
    :to="{ name: 'core.celery_progress', params: { taskId: task.meta.id } }"
  >
    <v-list-item-title>{{ task.meta.title }}</v-list-item-title>
    <v-list-item-subtitle>{{ task.meta.progressTitle }}</v-list-item-subtitle>

    <v-list-item-action>
      <v-progress-circular
        v-if="!task.complete"
        color="primary"
        :model-value="task.progress.percent"
      />
      <v-icon size="32px" v-else-if="task.state === 'SUCCESS'" color="success"
        >mdi-check-circle-outline</v-icon
      >
      <v-icon size="32px" v-else color="error">mdi-alert-circle-outline</v-icon>
    </v-list-item-action>
  </v-list-item>
</template>

<script>
export default {
  name: "TaskListItem",
  props: {
    task: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style scoped></style>
