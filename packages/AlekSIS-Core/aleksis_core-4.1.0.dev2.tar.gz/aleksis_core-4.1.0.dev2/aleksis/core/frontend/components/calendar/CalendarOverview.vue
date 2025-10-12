<script setup>
import TodoLists from "./todos/TodoLists.vue";
import IconButton from "../generic/buttons/IconButton.vue";
import CalendarSelect from "./CalendarSelect.vue";
import CalendarTypeSelect from "./CalendarTypeSelect.vue";
import CalendarViewSelect from "./CalendarViewSelect.vue";
import Calendar from "./Calendar.vue";
import CalendarDownloadAllButton from "./CalendarDownloadAllButton.vue";
import MainCalendarEventDialog from "./MainCalendarEventDialog.vue";
</script>

<template>
  <v-sheet class="mb-10">
    <main-calendar-event-dialog
      :initial-selected-event="presetEvent"
      @save="$refs.calendar.refresh()"
    >
      <template #activator="{ props: dialogProps, events }">
        <fab-button
          color="secondary"
          i18n-key="Create event"
          :icon-text="fabIcon"
        >
          <v-icon>{{ fabIcon }}</v-icon>
          <v-speed-dial
            v-model="fab"
            color="secondary"
            location="top center"
            activator="parent"
          >
            <v-btn
              v-for="(value, event) in events"
              :key="`chip-${event}`"
              size="small"
              @click="handleCreate(event, dialogProps, $event)"
              :color="value.color"
              :icon="value.iconText"
              v-tooltip="{
                text: $t(value.textKey),
                modelValue: $vuetify.display.mobile,
                nudgeLeft: $vuetify.display.mobile ? 20 : 0,
              }"
            />
          </v-speed-dial>
        </fab-button>
      </template>
    </main-calendar-event-dialog>
    <v-row align="stretch" class="page-height flex-nowrap">
      <div v-if="calendarView === 'calendar'">
        <v-navigation-drawer
          disable-route-watcher
          v-model="sidebar"
          lg="3"
          xl="2"
          :floating="$vuetify.display.lgAndUp"
          class="pt-6"
          :temporary="$vuetify.display.mdAndDown"
          :permanent="$vuetify.display.lgAndUp"
          width="300"
        >
          <!-- Mini date picker -->
          <v-date-picker
            id="side-picker"
            title=""
            v-model="calendarFocus"
            width="100%"
          ></v-date-picker>

          <!-- Calendar select (only desktop) -->
          <v-list>
            <v-list-subheader>
              {{ $t("calendar.my_calendars") }}
            </v-list-subheader>
            <calendar-select
              class="mb-4 overflow-auto"
              v-model="selectedCalendarFeedNames"
              :calendar-feeds="calendar.calendarFeeds"
              @input="storeActivatedCalendars"
            />
          </v-list>
          <template #append>
            <div class="pa-4 d-flex justify-center align-center">
              <v-spacer />
              <calendar-download-all-button
                v-if="calendar?.allFeedsUrl"
                :url="calendar.allFeedsUrl"
              />
              <v-spacer />
            </div>
          </template>
        </v-navigation-drawer>
      </div>
      <v-col
        :lg="calendarView === 'calendar' ? 9 : 12"
        :xl="calendarView === 'calendar' ? 10 : 12"
        class="d-flex flex-column fill-height"
      >
        <div class="d-flex justify-space-between flex-wrap mb-2 align-center">
          <!-- Calendar sidenav activator -->
          <icon-button
            v-if="$vuetify.display.mdAndDown && calendarView === 'calendar'"
            @click="sidebar = true"
            size="small"
            icon-text="mdi-menu"
            i18n-key="calendar.show_calendar_sidebar"
          />

          <v-spacer />

          <!-- Calendar type select (month, week, day) -->
          <calendar-type-select
            v-show="calendarView === 'calendar'"
            v-model="calendarType"
            class="mt-1 mt-md-0 mr-2"
          />

          <!-- Calendar view select (regular calendar, todos view) -->
          <calendar-view-select v-model="calendarView" class="mt-1 ma-md-0" />
        </div>
        <v-row class="overflow-auto calendar-height">
          <v-col class="fill-height">
            <!-- Actual calendar -->
            <calendar
              v-if="calendarView === 'calendar'"
              :focus="[calendarFocus]"
              @update:focus="([focus]) => (calendarFocus = focus)"
              v-model:type="calendarType"
              :calendar-feeds="selectedFeedsForCalendar"
              ref="calendar"
              height="100%"
              class="fill-height"
            />
            <!-- Todo lists -->
            <todo-lists v-else :calendar-feeds="todoFeeds" />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-sheet>
</template>

<script>
import { DateTime } from "luxon";

import calendarOverviewMixin from "./calendarOverviewMixin";
import calendarSelectedFeedsMixin from "./calendarSelectedFeedsMixin";

export default {
  name: "CalendarOverview",
  mixins: [calendarOverviewMixin, calendarSelectedFeedsMixin],
  methods: {
    handleCreate(calendarEvent, props, clickEvent) {
      this.presetEvent = calendarEvent;
      props.onClick(clickEvent);
    },
  },
  computed: {
    sidebar: {
      get() {
        return this.internalSidebar || this.$vuetify.display.lgAndUp;
      },
      set(value) {
        this.internalSidebar = value;
      },
    },
    fabIcon() {
      if (this.fab) {
        return "$close";
      }
      return "$plus";
    },
  },
  data() {
    return {
      internalSidebar: false,
      presetEvent: undefined,
      fab: false,
    };
  },
  mounted() {
    if (this.$route.name === "core.calendar_overview") {
      this.setCalendarFocus(DateTime.now());
      this.setCalendarType(this.$vuetify.display.mdAndDown ? "day" : "week");
    } else {
      // If we are here, we have a date supplied via the route params
      this.setCalendarFocus(
        DateTime.fromObject({
          year: this.$route.params.year,
          month: this.$route.params.month,
          day: this.$route.params.day,
        }),
      );
      this.setCalendarType(this.$route.params.view);
    }
  },
  watch: {
    calendarFocus(newValue, oldValue) {
      // Do not redirect on first page load
      if (!oldValue) return;

      const { year, month, day } = newValue;
      this.$router.push({
        name: "core.calendar_overview_with_params",
        params: {
          view: this.calendarType,
          year,
          month,
          day,
        },
      });
    },
    calendarType(newValue) {
      const { year, month, day } = this.calendarFocus;
      this.$router.push({
        name: "core.calendar_overview_with_params",
        params: {
          view: newValue,
          year,
          month,
          day,
        },
      });
    },
  },
};
</script>

<style scoped>
.page-height {
  /* not all browsers support dvh so we use vh as fallback */
  height: calc(98vh - 11rem);
  height: calc(100dvh - 11rem);
  overflow: auto;
}

.calendar-height {
  min-height: 400px;
}
</style>

<style>
#side-picker .v-picker-title {
  display: none;
}
</style>
