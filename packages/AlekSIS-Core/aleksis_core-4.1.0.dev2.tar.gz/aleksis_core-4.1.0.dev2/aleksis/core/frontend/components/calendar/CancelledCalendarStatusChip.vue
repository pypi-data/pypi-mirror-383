<script>
import CalendarStatusChip from "./CalendarStatusChip.vue";

export default {
  name: "CancelledCalendarStatusChip",
  components: { CalendarStatusChip },
};
</script>

<template>
  <calendar-status-chip icon="mdi-cancel" color="error">
    {{ $t("calendar.cancelled") }}
  </calendar-status-chip>
</template>
