<template>
  <v-list-item class="mx-4">
    <v-alert
      type="info"
      icon="mdi-calendar-remove-outline"
      variant="outlined"
      density="compact"
    >
      <v-row align="center" no-gutters>
        <v-col class="grow">
          <slot name="title">
            {{
              $t(
                "crud_components.infinite_scrolling_date_sorted_iterator.load.no_items",
                {
                  dateStart: $d(dateStart, "dateWithWeekday"),
                  dateEnd: $d(dateEnd, "dateWithWeekday"),
                },
              )
            }}
          </slot>
        </v-col>
        <v-spacer></v-spacer>
        <v-col class="shrink">
          <slot name="actions">
            <v-btn
              @click="
                $emit(
                  'loadMore',
                  loadMoreDateStart,
                  loadMoreDateEnd,
                  loadMoreDayIncrement,
                )
              "
              variant="outlined"
              size="small"
              color="info"
              :loading="loading"
            >
              {{
                $t(
                  "crud_components.infinite_scrolling_date_sorted_iterator.load.load_more",
                  { increment: loadMoreDayIncrement },
                )
              }}
            </v-btn>
          </slot>
        </v-col>
      </v-row>
    </v-alert>
  </v-list-item>
</template>
<script>
export default {
  name: "DateItemsLoadMore",
  props: {
    initialIncrement: {
      type: Number,
      required: false,
      default: null,
    },
    loadMoreDayIncrement: {
      type: Number,
      required: false,
      default: 30,
    },
    loadDirection: {
      type: String,
      required: true,
      validator(value, props) {
        return ["up", "down"].includes(value);
      },
    },
    date: {
      type: Object,
      required: true,
    },
    loading: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  emits: ["loadMore"],
  computed: {
    totalIncrement() {
      return this.initialIncrement
        ? this.initialIncrement
        : this.loadMoreDayIncrement;
    },
    dateStart() {
      return this.loadDirection === "up"
        ? this.date.minus({ days: this.totalIncrement })
        : this.date.plus({ days: 1 });
    },
    dateEnd() {
      return this.loadDirection === "up"
        ? this.date.minus({ days: 1 })
        : this.date.plus({ days: this.totalIncrement });
    },
    loadMoreDateStart() {
      return this.loadDirection === "up"
        ? this.date.minus({
            days: this.totalIncrement + this.loadMoreDayIncrement - 1,
          })
        : this.date.plus({ days: this.totalIncrement });
    },
    loadMoreDateEnd() {
      return this.loadDirection === "up"
        ? this.date.minus({ days: this.totalIncrement })
        : this.date.plus({
            days: this.totalIncrement + this.loadMoreDayIncrement - 1,
          });
    },
  },
};
</script>
