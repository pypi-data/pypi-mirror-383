<script setup>
import CRUDProvider from "./CRUDProvider.vue";
import CRUDIteratorEmptyMessage from "./CRUDIteratorEmptyMessage.vue";
import DateItemsLoader from "../DateItemsLoader.vue";
import DateSelectFooter from "../DateSelectFooter.vue";
import DateItemsLoadMore from "../DateItemsLoadMore.vue";

import { DateTime } from "luxon";
</script>

<template>
  <c-r-u-d-provider
    v-bind="$attrs"
    @last-query="lastQuery = $event"
    @items="handleItems"
    fixed-header
    disable-pagination
    hide-default-footer
    use-deep-search
    :gql-additional-query-args="gqlQueryArgsWithDates"
    ref="iterator"
  >
    <template #additionalActions="props">
      <slot name="additionalActions" v-bind="props" />
    </template>

    <template #filters="{ attrs, on }">
      <slot name="filters" :attrs="attrs" :on="on" />
    </template>

    <template #default>
      <date-items-loader v-if="!noItemsUp">
        <template #itemLoader>
          <slot name="itemLoader"></slot>
        </template>
      </date-items-loader>
      <date-items-load-more
        v-else-if="dateStart"
        load-direction="up"
        :date="dateStart"
        :initial-increment="lastIncrement"
        @load-more="loadUp"
      />

      <v-list-item
        class="px-1"
        lines="two"
        v-for="{ date, itemsOfDay } in groupedItems"
        v-intersect="{
          handler: intersectHandler(date),
          options: {
            rootMargin: '-' + topMargin + 'px 0px 0px 0px',
            threshold: [0, 1],
          },
        }"
        :key="'day-' + date"
        :date="date"
        ref="days"
      >
        <v-list-subheader
          class="text-h5 px-2 hover-hash"
          @click="gotoDate(date.toISODate())"
        >
          {{ $d(date, "dateWithWeekday") }}
        </v-list-subheader>
        <v-list max-width="100%" class="pt-0 mt-n1">
          <v-list-item
            class="px-1"
            v-for="item in itemsOfDay"
            :key="'item-' + (item.oldId || item.id)"
          >
            <slot name="item" :item="item" :last-query="lastQuery" />
          </v-list-item>
        </v-list>
      </v-list-item>

      <date-items-loader v-if="!noItemsDown">
        <template #itemLoader>
          <slot name="itemLoader"></slot>
        </template>
      </date-items-loader>
      <date-items-load-more
        v-else-if="dateEnd"
        load-direction="down"
        :date="dateEnd"
        :initial-increment="lastIncrement"
        @load-more="loadDown"
      />

      <date-select-footer
        :value="currentDate"
        @input="gotoDate"
        @prev="gotoPrev"
        @next="gotoNext"
      />
    </template>

    <template #loading>
      <slot name="loading">
        <date-items-loader :number-of-days="10" :number-of-docs="5">
          <template #itemLoader>
            <slot name="itemLoader"></slot>
          </template>
        </date-items-loader>
      </slot>
    </template>

    <template #no-data>
      <slot
        name="no-data"
        :date-start="dateStart"
        :date-end="dateEnd"
        @loadMore="loadMore"
      >
        <CRUDIteratorEmptyMessage
          :icon="emptyIcon"
          :load-more-button="true"
          :load-more-key="noDataLoadMoreKey"
          @load-more="loadMore"
        >
          {{
            $t(noDataTitleKey, {
              dateStart: $d(dateStart, "dateWithWeekday"),
              dateEnd: $d(dateEnd, "dateWithWeekday"),
            })
          }}
        </CRUDIteratorEmptyMessage>
      </slot>

      <date-select-footer
        :value="currentDate"
        @input="gotoDate"
        @prev="gotoPrev"
        @next="gotoNext"
      />
    </template>

    <template #no-results>
      <slot name="no-results">
        <CRUDIteratorEmptyMessage :icon="emptyIcon">
          {{ $t(noResultsTitleKey, { search: $refs.iterator.search }) }}
        </CRUDIteratorEmptyMessage>
      </slot>
    </template>
  </c-r-u-d-provider>
</template>

<script>
export default {
  name: "InfiniteScrollingDateSortedCRUDIterator",
  props: {
    /**
     * Number of consecutive days to load at once
     * This number of days is initially loaded and loaded
     * incrementally while scrolling.
     */
    dayIncrement: {
      type: Number,
      required: false,
      default: 7,
    },
    /**
     * Margin from list to top of viewport in pixels
     */
    topMargin: {
      type: Number,
      required: false,
      default: 165,
    },
    emptyIcon: {
      type: String,
      required: false,
      default: "mdi-magnify-remove-outline",
    },
    noDataTitleKey: {
      type: String,
      required: false,
      default: "crud_components.iterator_empty_message.no_data_with_dates",
    },
    noDataLoadMoreKey: {
      type: String,
      required: false,
      default: "crud_components.iterator_empty_message.load_more",
    },
    noResultsTitleKey: {
      type: String,
      required: false,
      default: "crud_components.iterator_empty_message.no_results",
    },
  },
  data() {
    return {
      lastQuery: null,
      // Next two: Indicates the currently fetched date range.
      dateStart: null,
      dateEnd: null,
      // Indicates whether component is ready for fetching more items.
      ready: false,
      // Date the component is initially called with.
      initDate: false,
      currentDate: "",
      // ID of requestIdleCallback queue used to update date value in URL hash.
      hashUpdater: false,
      // Next two: Indicates that initial attempt of loading up/down did not yield any results.
      noItemsUp: false,
      noItemsDown: false,
      // Increment used the last time items were loaded.
      lastIncrement: null,
      // ID of requestIdleCallback queue used to delay item fetching as long as the component is not ready yet.
      delayedFetch: false,
      // Next two: Indicates the first and last date currently displayed.
      firstDate: null,
      lastDate: null,
      groupedItems: [],
    };
  },
  methods: {
    handleItems(items) {
      this.groupedItems = this.groupItemsByDay(items);
      // Ensure that DOM is updated so that ref to days is present
      this.$nextTick(() => {
        if (this.initDate) {
          // Check if initDate matches any date of the fetched objects.
          // If yes, scroll to the section matching this date.
          // Only called when initDate is still set.
          if (
            this.groupedItems.some(
              (i) => i.date.toMillis() === this.initDate.toMillis(),
            )
          ) {
            this.$nextTick(this.gotoDate(this.initDate.toISODate(), "instant"));
          }
          this.transition();
        }
      });
    },
    resetDate(toDate) {
      console.log("Resetting date range", this.$route.hash);
      // Assure current date
      this.currentDate = toDate || this.$route.hash?.substring(1);
      if (!this.currentDate) {
        console.log("Set default date (current date)");
        this.setDate(DateTime.now().toISODate());
      }
      // Set initDate to passed date & the initial date range to be fetched.
      const date = DateTime.fromISO(this.currentDate);
      this.initDate = date;
      this.dateStart = date.minus({ days: this.dayIncrement });
      this.dateEnd = date.plus({ days: this.dayIncrement });
    },
    transition() {
      // Called when some day group matches the initDate
      // -> it gets reset since it is only needed to determine
      // which group to go to; and the component is now
      // ready to fetch more items.
      this.initDate = false;
      this.ready = true;
    },
    findDateSortedArrayLocation(itemDatetime, array, start, end) {
      const innerStart = start || 0;
      const innerEnd = end || array.length;
      const pivot = parseInt(innerStart + (innerEnd - innerStart) / 2);
      const pivotDatetime = DateTime.fromISO(array[pivot].datetimeStart);
      if (pivotDatetime.toMillis() === itemDatetime.toMillis()) {
        return pivot;
      } else if (pivotDatetime < itemDatetime) {
        if (innerEnd - innerStart <= 1) {
          return pivot + 1;
        }
        return this.findDateSortedArrayLocation(
          itemDatetime,
          array,
          pivot,
          innerEnd,
        );
      } else {
        if (innerEnd - innerStart <= 1) {
          return pivot;
        }
        return this.findDateSortedArrayLocation(
          itemDatetime,
          array,
          innerStart,
          pivot,
        );
      }
    },
    groupItemsByDay(items) {
      // Group items by date
      // => {dt: {date: dt, itemsOfDay: item ...} ...}
      const itemsByDay = items.reduce((byDay, item) => {
        const datetime = DateTime.fromISO(item.datetimeStart);
        const day = datetime.startOf("day");
        byDay[day] ??= { date: day, itemsOfDay: [] };
        if (byDay[day].itemsOfDay.length === 0) {
          byDay[day].itemsOfDay.push(item);
        } else {
          const index = this.findDateSortedArrayLocation(
            datetime,
            byDay[day].itemsOfDay,
          );
          byDay[day].itemsOfDay.splice(index, 0, item);
        }
        return byDay;
      }, {});
      // Determine for each item group whether its date
      // is the first and/or the last date available.
      // Sorting is necessary since backend can send items unordered
      // => [{date: dt, itemsOfDay: item ..., first: bool, last: bool} ...]
      return Object.keys(itemsByDay)
        .sort()
        .map((key, idx, { length }) => {
          const day = itemsByDay[key];
          if (idx === 0) {
            this.firstDate = day.date;
          }
          const lastIdx = length - 1;
          if (idx === lastIdx) {
            this.lastDate = day.date;
          }
          return day;
        });
    },
    fetchMore(from, to, then, noItems) {
      console.log("fetching", from, to);
      this.lastQuery.fetchMore({
        variables: {
          dateStart: from,
          dateEnd: to,
        },
        // Transform the previous result with new data
        // Additional operations performed are passed to this method
        updateQuery: (previousResult, { fetchMoreResult }) => {
          if (fetchMoreResult.items.length) {
            console.log("Received more");
            then();
          } else {
            console.log("No items received");
            noItems();
          }
          return { items: previousResult.items.concat(fetchMoreResult.items) };
        },
      });
    },
    refetchDay(date, then = () => {}) {
      console.log("refetching", date);
      this.lastQuery.fetchMore({
        variables: {
          dateStart: date,
          dateEnd: date,
        },
        // Transform the previous result with new data
        // Additional operations performed are passed to this method
        updateQuery: (previousResult, { fetchMoreResult }) => {
          console.log("Received new");
          then();
          // Exclude all items with same date from previous result and merge
          const filteredItems = previousResult.items.filter(
            (i) =>
              !DateTime.fromISO(i.datetimeStart).hasSame(
                DateTime.fromISO(date),
                "day",
              ),
          );
          return { items: filteredItems.concat(fetchMoreResult.items) };
        },
      });
    },
    setDate(date) {
      this.currentDate = date;
      // Replace the date in the URL's hash with the new date.
      // requestIdleCallback is used to delay this operation until
      // the browser is in an idle period.
      if (!this.hashUpdater) {
        this.hashUpdater = window.requestIdleCallback(() => {
          if (!(this.$route.hash.substring(1) === this.currentDate)) {
            this.$router.replace({ hash: this.currentDate });
          }
          this.hashUpdater = false;
        });
      }
    },
    fixScrollPos(height, top) {
      // Used to set the scrolled height after loading more items up.
      // Due to this being relative to the top, the extra height of
      // the new items needs to be set as a offset. nextTick is needed
      // due to the DOM likely being updated one tick after the items are
      // received. Only set ready to true after position was fixed.
      this.$nextTick(() => {
        if (height < document.documentElement.scrollHeight) {
          document.documentElement.scrollTop =
            document.documentElement.scrollHeight - height + top;
          this.ready = true;
        } else {
          // Try again, scrollTop have changed in the meantime.
          this.fixScrollPos(height, document.documentElement.scrollTop);
        }
      });
    },
    loadUp(dateStart, dateEnd, increment) {
      if (this.ready) {
        this.ready = false;
        this.noItemsUp = false;
        this.fetchMore(
          dateStart.toISODate(),
          dateEnd.toISODate(),
          // Callback function for the case that some items are received
          () => {
            this.noItemsUp = false;
            this.fixScrollPos(
              document.documentElement.scrollHeight,
              document.documentElement.scrollTop,
            );
            this.ready = true;
          },
          // Callback function for the case that no items are received
          () => {
            this.dateStart = dateEnd.plus({ days: 1 });
            this.lastIncrement = increment;
            this.noItemsUp = true;
            this.ready = true;
          },
        );
      } else {
        // If not ready for fetching yet, use an idle callback as heuristics to
        // determine when the previous fetching operation is most likely finished.
        console.log(
          "Not ready yet for fetching more data. Delaying operation.",
        );
        this.delayedFetch = window.requestIdleCallback(() => {
          this.loadUp(dateStart, dateEnd, increment);
          this.delayedFetch = false;
        });
      }
    },
    loadDown(dateStart, dateEnd, increment) {
      if (this.ready) {
        this.ready = false;
        this.noItemsDown = false;
        this.fetchMore(
          dateStart.toISODate(),
          dateEnd.toISODate(),
          // Callback function for the case that some items are received
          () => {
            this.noItemsDown = false;
            this.ready = true;
          },
          // Callback function for the case that no items are received
          () => {
            this.dateEnd = dateStart.minus({ days: 1 });
            this.lastIncrement = increment;
            this.noItemsDown = true;
            this.ready = true;
          },
        );
      } else {
        // If not ready for fetching yet, use an idle callback as heuristics to
        // determine when the previous fetching operation is most likely finished.
        console.log(
          "Not ready yet for fetching more data. Delaying operation.",
        );
        this.delayedFetch = window.requestIdleCallback(() => {
          this.loadDown(dateStart, dateEnd, increment);
          this.delayedFetch = false;
        });
      }
    },
    loadMore() {
      this.ready = true;
      this.loadUp(
        this.dateStart,
        this.dateStart.minus({ days: this.dayIncrement }),
        this.dayIncrement,
      );
      this.loadDown(
        this.dateEnd,
        this.dateEnd.plus({ days: this.dayIncrement }),
        this.dayIncrement,
      );
    },
    intersectHandler(date) {
      // Function returning a handler function called when a date group gets intersected.
      let once = true;
      return (entries) => {
        const entry = entries[0];
        if (entry.isIntersecting) {
          const first = date.toMillis() === this.firstDate.toMillis();

          if (entry.boundingClientRect.top <= this.topMargin) {
            // We are in the topmost date that is intersecting but already partly out of view
            // → focus on the next one, if there is a next one
            const newDate = this.findNext(date)?.toISODate();
            if (newDate) {
              console.log("@ ", newDate);
              this.setDate(newDate);
            }
          } else if (first) {
            // The element is still fully visible and the first one on the page → focus on it
            console.log("@ ", date.toISODate());
            this.setDate(date.toISODate());
          }

          if (once) {
            if (first) {
              // Load items from the increment time period before the
              // currently loaded date range when date group is first one.
              console.log("load up", date.toISODate());
              this.loadUp(
                date.minus({ days: this.dayIncrement }),
                date.minus({ days: 1 }),
                this.dayIncrement,
              );
            }
            if (date.toMillis() === this.lastDate.toMillis()) {
              // Load items from the increment time period after the
              // currently loaded date range down when date group is last one.
              console.log("load down", date.toISODate());
              this.loadDown(
                date.plus({ days: 1 }),
                date.plus({ days: this.dayIncrement }),
                this.dayIncrement,
              );
            }
            once = false;
          }
        }
      };
    },
    // The navigation logic could be a bit simpler if the current days
    // were known as a sorted array (= result of groupItemsByDay). But
    // then the list would need its own component and this gets rather
    // complicated. Then the calendar could also show the present days
    // / grey out the missing.
    //
    // Next two: arg date is ts object
    findPrev(date) {
      return this.$refs.days
        .map((day) => day.$attrs["date"])
        .sort()
        .reverse()
        .find((date2) => date2 < date);
    },
    findNext(date) {
      return this.$refs.days
        .map((day) => day.$attrs["date"])
        .sort()
        .find((date2) => date2 > date);
    },
    gotoDate(date, how = "smooth") {
      // Find existing date group matching the passed date.
      const existing = this.$refs.days.find(
        (day) => day.$attrs["date"].toISODate() === date,
      );

      if (existing) {
        // React immediatly -> smoother navigation
        // Also, intersect handler does not always react to scrollIntoView
        this.setDate(date);
        this.focus(existing, how);
      } else {
        const prev = this.findPrev(DateTime.fromISO(date));
        const next = this.findNext(DateTime.fromISO(date));
        if (prev && next) {
          // If passed date is between two existing days
          // -> go to the earlier one
          this.gotoDate(prev.toISODate());
        } else {
          // Outside existing day range
          // -> reset date range based on passed date
          // -> fetch for this new date range
          this.resetDate(date);
        }
      }
    },
    gotoPrev() {
      const prev = this.findPrev(DateTime.fromISO(this.currentDate));
      if (prev) {
        this.gotoDate(prev.toISODate());
      }
    },
    gotoNext() {
      const next = this.findNext(DateTime.fromISO(this.currentDate));
      if (next) {
        this.gotoDate(next.toISODate());
      }
    },
    focus(element, how = "smooth") {
      // Helper function used to scroll to day group.
      this.$vuetify.goTo(element, {
        duration: how === "instant" ? 0 : 400,
        offset: this.topMargin,
      });
    },
  },
  computed: {
    gqlQueryArgsWithDates() {
      return {
        ...this.$attrs["gql-additional-query-args"],
        dateStart: this.dateStart.toISODate(),
        dateEnd: this.dateEnd.toISODate(),
      };
    },
  },
  created() {
    // On creation, set some date values and the initial date range to be fetched.
    this.resetDate();
  },
};
</script>

<style scoped>
.hover-hash:hover::before {
  position: absolute;
  left: -1ch;
  content: "#";
}
</style>
