<script>
export default {
  name: "FilteredCalendarSelect",
  props: {
    modelValue: {
      type: [Object, Array],
      required: false,
      default: null,
    },
    types: {
      type: Object,
      required: true,
    },
    items: {
      type: Array,
      required: true,
    },
    searchPlaceholderKey: {
      type: String,
      required: false,
      default: "actions.search",
    },
    multiple: {
      type: Boolean,
      required: false,
      default: false,
    },
    itemUID: {
      type: String,
      required: false,
      default: "uid",
    },
    itemType: {
      type: String,
      required: false,
      default: "type",
    },
  },
  data() {
    return {
      innerSelected: [],
      search: "",
      selectedTypes: [],
    };
  },
  watch: {
    innerSelected(val) {
      this.$emit("update:modelValue", val);
    },
  },
  computed: {
    itemsFiltered() {
      // Filtered events by selected types
      return this.items.filter(
        (i) => this.selectedTypes.indexOf(i[this.itemType]) !== -1,
      );
    },
  },
  mounted() {
    this.selectedTypes = Object.keys(this.types);
  },
};
</script>

<template>
  <div>
    <v-card-text class="mb-0">
      <!-- Search field -->
      <v-text-field
        search
        variant="outlined"
        rounded
        clearable
        autofocus
        v-model="search"
        :placeholder="$t(searchPlaceholderKey)"
        prepend-inner-icon="mdi-magnify"
        hide-details="auto"
        class="mb-2"
      />

      <!-- Filter by event types -->
      <v-btn-toggle
        v-model="selectedTypes"
        density="compact"
        block
        multiple
        class="d-flex"
        variant="outlined"
      >
        <v-btn
          v-for="type in types"
          :key="type.id"
          class="flex-grow-1"
          :value="type.id"
        >
          {{ $t(type.nameKey) }}
        </v-btn>
      </v-btn-toggle>
    </v-card-text>

    <!-- Select groups of events -->
    <v-data-iterator
      :items="itemsFiltered"
      :item-key="itemUID"
      :search="search"
      single-expand
      :items-per-page="-1"
    >
      <template #default="{ items, isExpanded, expand }">
        <v-list
          class="scrollable-list"
          v-model:selected="innerSelected"
          :select-strategy="multiple ? 'leaf' : 'single-leaf'"
        >
          <v-list-item
            v-for="item in items"
            :value="item.raw"
            :key="item.raw[itemUID]"
          >
            <template #prepend>
              <v-icon v-if="types[item.raw[itemType]].icon" color="secondary">
                {{ types[item.raw[itemType]].icon }}
              </v-icon>
              <v-icon v-else color="secondary">mdi-grid</v-icon>
            </template>

            <v-list-item-title>{{
              item.raw[types[item.raw[itemType]].title]
            }}</v-list-item-title>

            <template #append="{ isSelected, select }" v-if="multiple">
              <v-list-item-action end>
                <v-checkbox-btn
                  :model-value="isSelected"
                  @update:model-value="select"
                />
              </v-list-item-action>
            </template>
          </v-list-item>
        </v-list>
      </template>
    </v-data-iterator>
  </div>
</template>

<style scoped>
.scrollable-list {
  height: 100%;
  overflow-y: scroll;
}
</style>
