<script>
export default {
  name: "CalendarControlBar",
  emits: ["prev", "next", "today"],
  props: {
    small: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
};
</script>

<template>
  <div class="d-flex justify-center mx-2">
    <icon-button
      @click="$emit('prev')"
      :small="small"
      icon-text="$prev"
      i18n-key="actions.scroll_prev"
    />
    <v-btn
      variant="outlined"
      class="mx-1"
      @click="$emit('today')"
      :small="small"
    >
      {{ $t("calendar.today") }}
    </v-btn>
    <icon-button
      @click="$emit('next')"
      :small="small"
      icon-text="$next"
      i18n-key="actions.scroll_next"
    />
  </div>
</template>
