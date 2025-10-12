<template>
  <v-img :src="fileName" :class="{ rotating: rotate }" v-bind="$attrs" />
</template>

<script>
export default {
  name: "Mascot",
  data() {
    return {
      types: [
        {
          type: "default",
          file: "/static/img/mascot/mascot.svg",
        },
        {
          type: "broken",
          file: "/static/img/mascot/mascot_broken.svg",
        },
        {
          type: "forbidden",
          file: "/static/img/mascot/mascot_forbidden.svg",
        },
        {
          type: "no_notifications",
          file: "/static/img/mascot/mascot_no_notifications.svg",
        },
        {
          type: "not_found",
          file: "/static/img/mascot/mascot_not_found.svg",
        },
        {
          type: "not_ok",
          file: "/static/img/mascot/mascot_not_ok.svg",
        },
        {
          type: "offline",
          file: "/static/img/mascot/mascot_offline.svg",
        },
        {
          type: "ok",
          file: "/static/img/mascot/mascot_ok.svg",
        },
        {
          type: "question",
          file: "/static/img/mascot/mascot_question.svg",
        },
        {
          type: "ready_for_items",
          file: "/static/img/mascot/mascot_ready_for_items.svg",
        },
        {
          type: "searching",
          file: "/static/img/mascot/mascot_searching.svg",
        },
        {
          type: "success_off",
          file: "/static/img/mascot/mascot_success_off.svg",
        },
        {
          type: "success_on",
          file: "/static/img/mascot/mascot_success_on.svg",
        },
        {
          type: "timetable",
          file: "/static/img/mascot/mascot_timetable.svg",
        },
      ],
    };
  },
  props: {
    type: {
      type: String,
      required: false,
      default: "default",
    },
    rotate: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  computed: {
    fileName() {
      return this.types.find((t) => t.type === this.type).file;
    },
  },
};
</script>

<style>
.rotating {
  overflow: hidden;
  transition-duration: 0.8s;
  transition-property: transform;
}
.rotating:hover,
.rotating:active {
  transform: rotate(360deg);
  -webkit-transform: rotate(360deg);
}
</style>
