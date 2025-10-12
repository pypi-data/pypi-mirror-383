<template>
  <v-bottom-sheet
    :value="show"
    persistent
    hide-overlay
    max-width="400px"
    ref="sheet"
  >
    <v-expansion-panels variant="accordion" v-model="open">
      <v-expansion-panel>
        <v-expansion-panel-title color="primary" class="px-4">
          {{
            $t("celery_progress.running_tasks", numberOfTasks, {
              number: numberOfTasks,
            })
          }}
          <template #actions>
            <v-icon color="on-primary"> mdi-chevron-up </v-icon>
          </template>
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <div class="mx-n6 mb-n4" v-if="celeryProgressByUser">
            <task-list-item
              v-for="task in celeryProgressByUser"
              :task="task"
              :key="task.meta.id"
            />
          </div>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-bottom-sheet>
</template>

<script>
import TaskListItem from "./TaskListItem.vue";
import gqlCeleryProgressButton from "./celeryProgressBottom.graphql";

const NORMAL_INTERVAL = 30000;
const FREQUENT_INTERVAL = 1000;

export default {
  name: "CeleryProgressBottom",
  components: { TaskListItem },
  data() {
    return { open: 0 };
  },
  mounted() {
    // Vuetify uses the hideScroll method to disable scrolling by setting an event listener
    // to the window. As event listeners can only be removed by referencing the listener
    // method and because vuetify this method is called on every state change of the dialog,
    // we simply replace the method in this component instance
    this.$refs.sheet.hideScroll = this.$refs.sheet.showScroll;
  },
  watch: {
    "$root.frequentCeleryPolling": function (newValue) {
      // Watch for activation of frequent polling and update poll interval accordingly

      const newInterval = newValue ? FREQUENT_INTERVAL : NORMAL_INTERVAL;
      if (
        this.$apollo.queries.celeryProgressByUser.options.pollInterval !==
        newInterval
      ) {
        this.$apollo.queries.celeryProgressByUser.stopPolling();
        this.$apollo.queries.celeryProgressByUser.options.pollInterval =
          newInterval;
        this.$apollo.queries.celeryProgressByUser.startPolling(newInterval);
      }
    },
  },
  computed: {
    show() {
      return this.celeryProgressByUser && this.celeryProgressByUser.length > 0;
    },
    numberOfTasks() {
      if (!this.celeryProgressByUser) {
        return 0;
      }
      return this.celeryProgressByUser.length;
    },
  },
  apollo: {
    celeryProgressByUser: {
      query: gqlCeleryProgressButton,
      pollInterval: NORMAL_INTERVAL,
      result({ data }) {
        // Deactivate frequent polling if there is not at least one running task
        this.$root.frequentCeleryPolling = data.celeryProgressByUser.length > 0;
      },
    },
  },
};
</script>
