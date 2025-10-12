<script setup>
import CRUDProvider from "./CRUDProvider.vue";

defineProps({
  type: {
    type: String,
    required: true,
  },
  nameProp: {
    type: [String, Function],
    required: false,
    default: "name",
  },
});

defineEmits(["promptCreate"]);
</script>

<template>
  <c-r-u-d-provider
    :object-schema="{ type }"
    v-bind="$attrs"
    disable-patch
    disable-delete
  >
    <template v-for="(_, slot) of $slots" #[slot]="props">
      <slot :name="slot" v-bind="props" />
    </template>

    <template
      #body="{
        queryItems,
        objectSchema,
        loading,
        disableCreate,
        onPromptCreate,
      }"
    >
      <v-autocomplete
        class="fc-my-auto"
        v-bind="$attrs"
        :items="queryItems"
        item-value="id"
        :item-title="nameProp"
        :loading="loading"
        hide-no-data
        :chips="$attrs?.multiple"
      >
        <template #append v-if="!disableCreate">
          <icon-button
            icon-text="$plus"
            i18n-key="actions.create"
            @click="onPromptCreate()"
          />
        </template>

        <template #item="{ props, item }">
          <v-list-item
            v-bind="props"
            :title="
              !objectSchema.displayComponent || objectSchema.type == 'array'
                ? props.title
                : undefined
            "
          >
            <component
              v-if="
                objectSchema.displayComponent && objectSchema.type != 'array'
              "
              :is="objectSchema.displayComponent"
              :value="item.raw"
              :object-schema="objectSchema"
            />
          </v-list-item>
        </template>

        <template #chip="{ item }">
          <component
            v-if="objectSchema.displayComponent && objectSchema.type != 'array'"
            :is="objectSchema.displayComponent"
            :value="item.raw"
            :object-schema="objectSchema"
          />
          <template v-else>{{ item.title }}</template>
        </template>

        <!-- TODO: Be more precise here? -->
        <template v-for="(_, slot) of $slots" #[slot]="props">
          <slot :name="slot" v-bind="props" />
        </template>
      </v-autocomplete>
    </template>
  </c-r-u-d-provider>
</template>

<style scoped>
.fc-my-auto > :first-child {
  margin-block: auto;
}
</style>
