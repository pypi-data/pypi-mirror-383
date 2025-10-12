<script>
export default {
  name: "SlideIterator",
  extends: "v-data-iterator",
  emits: ["update:isExpanded"],
  data() {
    return {
      expanded: [],
      selected: [],
    };
  },
  props: {
    itemKeyGetter: {
      type: Function,
      default: (item) => item.id,
      required: false,
    },
    loading: {
      type: Boolean,
      default: false,
      required: false,
    },
    loadOnlySelected: {
      type: Boolean,
      default: false,
      required: false,
    },
    disabled: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  watch: {
    /**
     * Emits an event when items are expanded or not anymore.
     *
     * @param newValue new list of expanded items
     * @param oldValue previous list of expanded items
     */
    expanded(newValue, oldValue) {
      const n = newValue.length > 0;
      const o = oldValue.length > 0;

      if (n === o) {
        // Only emit an event when the length is different
        return;
      }

      if (n) {
        // At least one item is now expanded and previously there were none
        this.$emit("update:isExpanded", true);
        return;
      }

      // no item is expanded anymore
      this.$emit("update:isExpanded", false);
    },
  },
};
</script>

<template>
  <v-data-iterator
    disable-pagination
    hide-default-footer
    single-expand
    v-model:expanded="expanded"
    v-model="selected"
    v-bind="$attrs"
    :loading="loading"
  >
    <template #default="{ items, isSelected, expand, select }">
      <v-slide-x-transition leave-absolute>
        <v-list v-show="expanded.length === 0">
          <v-list-item
            v-for="item in items"
            :key="itemKeyGetter(item)"
            :value="item"
            :disabled="disabled || loading"
            :active="isSelected(item)"
            @click.stop.exact="expand(item, true)"
          >
            <template #prepend="{ isSelected }">
              <v-list-item-action start>
                <v-scale-transition leave-absolute>
                  <v-progress-circular
                    v-if="loading && (isSelected || !loadOnlySelected)"
                    indeterminate
                    :size="20"
                    :width="2"
                    color="primary"
                  />
                  <v-checkbox
                    v-else
                    :model-value="isSelected"
                    :disabled="disabled || loading"
                    color="primary"
                    @click.stop
                    @update:model-value="select(item, $event)"
                  />
                </v-scale-transition>
              </v-list-item-action>
            </template>

            <slot name="listItemContent" :item="item" :selected="selected" />

            <v-list-item-action>
              <icon-button
                large
                :disabled="disabled"
                icon-text="$next"
                i18n-key="actions.open_details"
              />
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-slide-x-transition>
      <v-slide-x-reverse-transition leave-absolute>
        <v-card v-if="expanded.length > 0">
          <slot
            name="expandedItem"
            :item="expanded[0]"
            :close="() => expand(expanded[0], false)"
          >
            <v-card-title>
              {{ $t("selection.num_items_selected", expanded.length) }}
            </v-card-title>
            <v-card-text>
              <p>{{ expanded[0] }}</p>
              <secondary-action-button
                @click="expand(expanded[0], false)"
                i18n-key="actions.close"
              />
            </v-card-text>
          </slot>
        </v-card>
      </v-slide-x-reverse-transition>
    </template>
    <template #loading>
      <v-skeleton-loader type="list-item-avatar@6" />
    </template>
  </v-data-iterator>
</template>

<style scoped></style>
