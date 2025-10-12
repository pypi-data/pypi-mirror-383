<template>
  <v-sheet class="fullsize" @click="$emit('toggle')" :border="selected">
    <v-overlay
      contained
      :model-value="selected"
      class="align-center justify-center"
    >
      <div class="grid">
        <div class="up">
          <primary-action-button
            @click="resize(0, -1, 0, 1)"
            icon
            :disabled="!canGoUp"
            icon-text="mdi-arrow-expand-up"
            i18n-key="actions.expand.up"
          />
          <primary-action-button
            @click="resize(0, 1, 0, -1)"
            icon
            :disabled="widget.h <= 1"
            icon-text="mdi-arrow-collapse-down"
            i18n-key="actions.collapse.down"
          />
        </div>

        <!-- eslint-disable-next-line vuetify/no-deprecated-classes -->
        <div class="left">
          <primary-action-button
            @click="resize(-1, 0, 1, 0)"
            icon
            :disabled="!canGoLeft"
            icon-text="mdi-arrow-expand-left"
            i18n-key="actions.expand.left"
          />
          <primary-action-button
            @click="resize(1, 0, -1, 0)"
            icon
            :disabled="widget.w <= 1"
            icon-text="mdi-arrow-collapse-right"
            i18n-key="actions.collapse.right"
          />
        </div>

        <div class="delete">
          <secondary-action-button
            icon
            small
            color="error"
            fab
            i18n-key="actions.delete"
            icon-text="$deleteContent"
            fixed
            :loading="deleteLoading"
            @click="performDelete"
          />
        </div>
        <!-- eslint-disable-next-line vuetify/no-deprecated-classes -->
        <div class="right">
          <primary-action-button
            @click="resize(0, 0, 1, 0)"
            icon
            :disabled="!canGoRight"
            icon-text="mdi-arrow-expand-right"
            i18n-key="actions.expand.right"
          />
          <primary-action-button
            @click="resize(0, 0, -1, 0)"
            icon
            :disabled="widget.w <= 1"
            icon-text="mdi-arrow-collapse-left"
            i18n-key="actions.collapse.left"
          />
        </div>
        <div class="down">
          <primary-action-button
            @click="resize(0, 0, 0, 1)"
            icon
            :disabled="!canGoDown"
            icon-text="mdi-arrow-expand-down"
            i18n-key="actions.expand.down"
          />
          <primary-action-button
            @click="resize(0, 0, 0, -1)"
            icon
            :disabled="widget.h <= 1"
            icon-text="mdi-arrow-collapse-up"
            i18n-key="actions.collapse.up"
          />
        </div>
      </div>
    </v-overlay>

    <component :is="component" v-bind="widget.data" class="fullsize" />
  </v-sheet>
</template>

<script setup>
import { useCRUD } from "../../../composables/crud/useCRUD";
import { defineEmits, defineProps, computed } from "vue";
import { deleteDashboardWidgetInstances } from "./manageDashboard.graphql";
import { buildQuery } from "../dashboardQuery";

const $emit = defineEmits(["toggle", "reposition"]);
const props = defineProps({
  widget: {
    type: Object,
    required: true,
  },
  selected: {
    type: Boolean,
    required: false,
    default: false,
  },
  component: {
    type: [String, Object, Function],
    required: true,
  },
  positionAllowed: {
    type: [Function],
    required: false,
    default: (x, y, key) => false,
  },
});

const { delete: deleteFn, deleteLoading } = useCRUD({
  deleteMutation: deleteDashboardWidgetInstances,
  query: buildQuery(),
});

function performDelete() {
  deleteFn({ ids: [props.widget.data.id] });
}

function resize(deltaX, deltaY, deltaW, deltaH) {
  $emit("reposition", {
    ...props.widget,
    x: props.widget.x + deltaX,
    y: props.widget.y + deltaY,
    w: props.widget.w + deltaW,
    h: props.widget.h + deltaH,
  });
}

const canGoLeft = computed(() => {
  const x = props.widget.x - 1;
  for (let yOffset = 0; yOffset < props.widget.h; yOffset++) {
    let y = props.widget.y + yOffset;
    if (!props.positionAllowed(x, y, props.widget.key)) {
      return false;
    }
  }

  return true;
});

const canGoRight = computed(() => {
  const x = props.widget.x + props.widget.w;
  for (let yOffset = 0; yOffset < props.widget.h; yOffset++) {
    let y = props.widget.y + yOffset;
    if (!props.positionAllowed(x, y, props.widget.key)) {
      return false;
    }
  }

  return true;
});

const canGoUp = computed(() => {
  const y = props.widget.y - 1;
  for (let xOffset = 0; xOffset < props.widget.w; xOffset++) {
    let x = props.widget.x + xOffset;
    if (!props.positionAllowed(x, y, props.widget.key)) {
      return false;
    }
  }

  return true;
});

const canGoDown = computed(() => {
  const y = props.widget.y + props.widget.h;
  for (let xOffset = 0; xOffset < props.widget.w; xOffset++) {
    let x = props.widget.x + xOffset;
    if (!props.positionAllowed(x, y, props.widget.key)) {
      return false;
    }
  }

  return true;
});
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  grid-template-rows: 1fr 2fr 1fr;
  grid-template-areas: ". up ." "left delete right" ". down .";
}
.grid > div {
  display: flex;
  align-items: center;
  justify-content: center;
}
.grid > .left,
.grid > .right {
  flex-direction: column;
}
.grid > .up {
  grid-area: up;
}
.grid > .down {
  grid-area: down;
}
.grid > .left {
  grid-area: left;
}
.grid > .right {
  grid-area: right;
}
.grid > .delete {
  grid-area: delete;
}
</style>
