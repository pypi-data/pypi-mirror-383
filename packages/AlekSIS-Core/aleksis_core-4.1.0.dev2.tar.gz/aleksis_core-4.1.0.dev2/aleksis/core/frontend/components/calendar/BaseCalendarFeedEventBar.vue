<template>
  <div
    class="text-truncate fullsize"
    :class="{
      'text-decoration-line-through': event.status === 'CANCELLED',
      'mx-1': withPadding,
    }"
    :style="{ height: '100%' }"
  >
    <slot name="time" v-bind="$props">
      <span
        v-if="
          calendarType === 'month' && eventParsed.start.hasTime && !withoutTime
        "
        class="mr-1 font-weight-bold ml-1"
      >
        {{ eventParsed.start.time }}
      </span>
    </slot>
    <slot name="icon" v-bind="$props">
      <v-icon v-if="icon" size="x-small" color="white" class="mx-1 float-left">
        {{ icon }}
      </v-icon>
    </slot>

    <slot name="title" v-bind="$props">
      {{ event.name }}
    </slot>
  </div>
</template>

<script>
import calendarFeedEventBarMixin from "../../mixins/calendarFeedEventBar.js";

export default {
  name: "BaseCalendarFeedEventBar",
  mixins: [calendarFeedEventBarMixin],
  props: {
    withPadding: {
      required: false,
      type: Boolean,
      default: true,
    },
    icon: {
      required: false,
      type: String,
      default: "",
    },
    withoutTime: {
      required: false,
      type: Boolean,
      default: false,
    },
  },
};
</script>
